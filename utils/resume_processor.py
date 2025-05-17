import os
import logging
import traceback
import json

from utils.gemini_api import GeminiAPI
import PyPDF2
import docx
from config import Config
import fitz
import easyocr
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResumeProcessor:
    def __init__(self):
        try:
            self.gemini_api = GeminiAPI()
            # Initialize EasyOCR reader once during startup
            self.reader = easyocr.Reader(['en'])  # Initialize with English language
            logger.info("ResumeProcessor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ResumeProcessor: {e}")
            traceback.print_exc()
            raise

    def extract_text_with_easyocr(self, image_path):
        try:
            # Use EasyOCR to extract text
            result = self.reader.readtext(image_path)
            # Combine all detected text
            text = ' '.join([text_result[1] for text_result in result])
            return text
        except Exception as e:
            logger.error(f"Error in EasyOCR processing: {e}")
            traceback.print_exc()
            return f"Error processing with EasyOCR: {str(e)}"

    def pdf_to_images(self, pdf_path, output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            doc = fitz.open(pdf_path)
            image_paths = []

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5))
                image_path = os.path.join(output_dir, f"page_{page_num + 1}.png")
                pix.save(image_path)
                image_paths.append(image_path)

            doc.close()
            return image_paths
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            traceback.print_exc()
            return []

    def extract_text(self, resume_file):
        temp_dir = Config.UPLOAD_FOLDER
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, resume_file.filename)
        resume_file.save(temp_path)

        try:
            file_ext = os.path.splitext(resume_file.filename)[1].lower()
            text = ""

            if file_ext == '.pdf':
                # Try with PyMuPDF (fitz) first instead of PyPDF2
                try:
                    pdf_doc = fitz.open(temp_path)
                    for page_num in range(len(pdf_doc)):
                        page = pdf_doc[page_num]
                        page_text = page.get_text()
                        if page_text:
                            text += page_text + "\n"
                    pdf_doc.close()
                except Exception as fitz_error:
                    logger.error(f"PyMuPDF extraction error: {fitz_error}")
                    traceback.print_exc()

                    # Fall back to PyPDF2 if PyMuPDF fails
                    try:
                        with open(temp_path, 'rb') as file:
                            reader = PyPDF2.PdfReader(file)
                            for page in reader.pages:
                                try:
                                    page_text = page.extract_text()
                                    if page_text:
                                        text += page_text + "\n"
                                except Exception as page_error:
                                    logger.warning(f"Error extracting text from page: {page_error}")
                                    continue  # Skip problematic pages
                    except Exception as pypdf_error:
                        logger.error(f"PyPDF2 extraction error: {pypdf_error}")
                        traceback.print_exc()

                # If text extraction failed or returned minimal text, use OCR
                if not text.strip() or len(text) < 100:
                    logger.info("Text extraction insufficient, falling back to OCR")
                    images_dir = os.path.join(temp_dir, "pdf_images")
                    image_paths = self.pdf_to_images(temp_path, images_dir)
                    ocr_text = ""

                    for img_path in image_paths:
                        # Use EasyOCR instead of Tesseract
                        page_text = self.extract_text_with_easyocr(img_path)
                        ocr_text += page_text + "\n"
                        try:
                            os.remove(img_path)
                        except Exception:
                            logger.warning(f"Failed to remove temporary image: {img_path}")

                    if ocr_text.strip():
                        text = ocr_text

                    try:
                        os.rmdir(images_dir)
                    except Exception:
                        logger.warning(f"Failed to remove images dir: {images_dir}")

            elif file_ext in ['.docx', '.doc']:
                try:
                    doc = docx.Document(temp_path)
                    text = "\n".join([p.text for p in doc.paragraphs if p.text])
                except Exception as docx_error:
                    logger.error(f"DOCX processing error: {docx_error}")
                    traceback.print_exc()
                    return f"Error extracting text from Word document: {str(docx_error)}"

            elif file_ext in ['.txt', '.rtf']:
                try:
                    with open(temp_path, 'r', encoding='utf-8', errors='ignore') as file:
                        text = file.read()
                except Exception as txt_error:
                    logger.error(f"TXT processing error: {txt_error}")
                    traceback.print_exc()
                    return f"Error extracting text from text file: {str(txt_error)}"

            elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
                # Use EasyOCR for image files
                text = self.extract_text_with_easyocr(temp_path)

            else:
                msg = f"Unsupported file format: {file_ext}. Please upload PDF, DOCX, TXT, or image files."
                logger.warning(msg)
                return msg

            if not text.strip():
                msg = "Error: Could not extract any text from the document."
                logger.warning(msg)
                return msg

            logger.info(f"Successfully extracted {len(text)} characters from resume")
            return text

        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            traceback.print_exc()
            return f"Error extracting text: {str(e)}"

        finally:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    logger.info(f"Removed temporary file: {temp_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file: {e}")

    # The rest of your code remains unchanged
    def generate_ai_recommendations(self, analysis_results, job_description):
        """
        Generate AI-powered recommendations based on resume analysis results

        Args:
            analysis_results: Dictionary containing resume analysis
            job_description: Job description string

        Returns:
            list: List of actionable recommendations
        """
        recommendations = []

        # Calculate match quality
        match_score = analysis_results.get('match_score', 0)
        experience_match = analysis_results.get('experience_match', False)
        skills_matched = analysis_results.get('skills_matched', [])
        skills_missing = analysis_results.get('skills_missing', [])

        # Generate recommendations based on match score
        if match_score >= 85:
            recommendations.append("Strong candidate match. Proceed to interview stage with standard process.")
        elif match_score >= 70:
            recommendations.append("Good candidate match. Consider a technical assessment before interview.")
        elif match_score >= 50:
            recommendations.append(
                "Moderate candidate match. Consider a preliminary screening call to assess potential.")
        else:
            recommendations.append(
                "Low match score. Consider other candidates or explore if candidate has transferable skills not captured in the analysis.")

        # Experience recommendations
        if not experience_match:
            recommendations.append(
                "Experience gap detected. If proceeding with candidate, prepare specific questions about relevant projects and practical applications.")

        # Skills recommendations
        if len(skills_missing) > 0:
            # If certain critical skills are missing
            if any(skill in ["Business Analysis", "Project Management", "Leadership"] for skill in skills_missing):
                recommendations.append(
                    f"Missing critical skills: {', '.join([s for s in skills_missing if s in ['Business Analysis', 'Project Management', 'Leadership']])}. Consider assessing adaptability and learning capacity.")

            # If technical skills are missing
            tech_skills = [s for s in skills_missing if
                           s not in ["Business Analysis", "Project Management", "Leadership"]]
            if tech_skills:
                recommendations.append(f"Consider technical assessment focused on: {', '.join(tech_skills[:3])}.")

        # If the match is good but something is missing
        if match_score >= 70 and (not experience_match or len(skills_missing) > 0):
            recommendations.append(
                "Candidate shows strong potential despite gaps. Consider assessing cultural fit and growth mindset.")

        # If we have no substantive recommendations yet
        if len(recommendations) <= 2:
            recommendations.append(
                "Review candidate's communication skills and problem-solving approach during interview.")

        return recommendations

    def process(self, resume_file, job_description):
        try:
            resume_text = self.extract_text(resume_file)

            if isinstance(resume_text, str) and (
                    resume_text.startswith("Error") or resume_text.startswith("Unsupported")):
                logger.error(f"Extraction error: {resume_text}")
                return {"error": resume_text, "status": "failed"}

            results = self.gemini_api.analyze_resume(resume_text, job_description)

            if isinstance(results, dict):
                # Add file metadata
                results["file_name"] = resume_file.filename
                results["resume_text_preview"] = resume_text[:200] + "..." if len(resume_text) > 200 else resume_text

                # Generate AI recommendations
                recommendations = self.generate_ai_recommendations(results, job_description)
                results["recommendations"] = recommendations

                # Add a simple score if missing
                if "match_score" not in results:
                    # Calculate a simple score based on skills match
                    skills_matched = len(results.get("skills_matched", []))
                    skills_missing = len(results.get("skills_missing", []))
                    total_skills = skills_matched + skills_missing
                    if total_skills > 0:
                        results["match_score"] = int((skills_matched / total_skills) * 100)
                    else:
                        results["match_score"] = 50  # Default score

                results["status"] = "success"
            else:
                results = {
                    "analysis": results,
                    "file_name": resume_file.filename,
                    "resume_text_preview": resume_text[:200] + "..." if len(resume_text) > 200 else resume_text,
                    "status": "success"
                }

            return results

        except Exception as e:
            logger.error(f"Resume processing failed: {e}")
            traceback.print_exc()
            return {"error": str(e), "status": "failed"}
