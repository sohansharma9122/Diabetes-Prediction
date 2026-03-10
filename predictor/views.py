from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os, re, cv2, numpy as np, pytesseract, requests
from pdf2image import convert_from_path
from PIL import Image

# ✅ Path to Tesseract (change if installed elsewhere)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ✅ Path to Poppler (needed for PDF to Image conversion)
POPPLER_PATH = r"C:\Users\HP\Downloads\Release-25.07.0-0\poppler-25.07.0\Library\bin"

# Import ML model
from .ml_model import predict_for_input, lg


# -------------------------------
# Utility: Clean OCR text
# -------------------------------
def clean_text(text):
    lines = text.split('\n')
    cleaned = [line.strip() for line in lines if line.strip()]
    return '\n'.join(cleaned)


# -------------------------------
# Utility: Extract numeric value near a keyword
# -------------------------------
def find_value(keyword, text):
    if not text:
        return None

    # Handles keywords like "Blood Pressure: 120/80"
    pattern_bp = r"(?:blood pressure|bp)[^0-9]{0,10}([0-9]{2,3})[^\d]{0,3}([0-9]{2,3})"
    if re.search(pattern_bp, text, re.IGNORECASE) and keyword.lower() in ["blood pressure", "bp"]:
        match = re.search(pattern_bp, text, re.IGNORECASE)
        if match:
            try:
                return (float(match.group(1)) + float(match.group(2))) / 2
            except:
                pass

    pattern1 = rf"{keyword}[^0-9\n\r]{{0,20}}([0-9]+(?:\.[0-9]+)?)"
    pattern2 = rf"([0-9]+(?:\.[0-9]+)?)[^0-9\n\r]{{0,20}}{keyword}"

    m = re.search(pattern1, text, re.IGNORECASE)
    if not m:
        m = re.search(pattern2, text, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except:
            return None
    return None


# -------------------------------
# ✅ Improved Age extraction (Final Fix)
# -------------------------------
def find_age(text):
    """
    Extracts age correctly even if OCR misreads characters like O→0 or I→1.
    Handles:
      - Age: 45
      - Age - 54 years
      - 54 yrs / 54Y / 54 years
      - Age : 6O (OCR 'O' mistaken for zero)
    """
    if not text:
        return None

    # Clean OCR confusion
    fixed_text = (
        text.replace("O", "0")
        .replace("o", "0")
        .replace("|", "1")
        .replace("I", "1")
        .replace("l", "1")
    )

    # Pattern 1: Age: 45 or Age - 54 years
    m = re.search(r'Age[^0-9]{0,6}([0-9][0-9\s\.]{0,4})', fixed_text, re.IGNORECASE)
    if not m:
        # Pattern 2: 45 yrs / 45 years / 45y / 45 Y
        m = re.search(r'([0-9][0-9\s\.]{0,4})\s*(yrs?|years?|y)', fixed_text, re.IGNORECASE)

    if m:
        raw_age = m.group(1)
        # Remove spaces or dots like “5 6” → “56”
        age_str = re.sub(r'[^0-9]', '', raw_age)
        try:
            age = int(age_str)
            if 1 <= age <= 120:
                return float(age)
        except:
            pass
    return None


# -------------------------------
# Manual prediction form
# -------------------------------
def predict(request):
    if 'Email' not in request.session:
        return redirect('login')

    if request.method == "POST":
        glucose = float(request.POST.get('glucose') or 0)
        bp = float(request.POST.get('bp') or 0)
        skin = float(request.POST.get('skin') or 0)
        insulin = float(request.POST.get('insulin') or 0)
        bmi = float(request.POST.get('bmi') or 0)
        preg = float(request.POST.get('preg') or 0)
        pedigree = float(request.POST.get('pedigree') or 0)
        age = float(request.POST.get('age') or 0)

        try:
            lg()
        except Exception as e:
            print("Model training skipped/error:", e)

        try:
            result_code = predict_for_input(glucose, bp, skin, insulin, bmi, preg, pedigree, age)
            result_code = int(result_code[0]) if isinstance(result_code, (list, tuple)) else int(result_code)
        except Exception as e:
            return render(request, 'result.html', {'result': f'Prediction failed: {e}'})

        msg = "⚠️ Possible Diabetes — please consult a doctor." if result_code == 1 else "✅ No Diabetes detected."

        map_url = None
        if result_code == 1:
            try:
                ip_info = requests.get("https://ipinfo.io/json", timeout=3).json()
                city = ip_info.get('city', 'your area')
                map_url = f"https://www.google.com/maps/search/diabetes+doctor+near+{city}"
            except:
                map_url = "https://www.google.com/maps/search/diabetes+doctor+near+me"

        return render(request, 'result.html', {'result': msg, 'map_url': map_url})

    return render(request, 'predict.html')


# -------------------------------
# Upload Report (PDF/Image) + OCR + ML Prediction
# -------------------------------
def upload_report(request):
    if 'Email' not in request.session:
        return redirect('login')

    if request.method == "POST" and request.FILES.get('report'):
        uploaded_file = request.FILES['report']

        # ✅ Save uploaded file
        save_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        os.makedirs(save_dir, exist_ok=True)
        fs = FileSystemStorage(location=save_dir)
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)

        images = []

        # ✅ Convert PDF to images
        if uploaded_file.name.lower().endswith('.pdf'):
            try:
                pil_images = convert_from_path(file_path, poppler_path=POPPLER_PATH)
                for p in pil_images:
                    images.append(cv2.cvtColor(np.array(p), cv2.COLOR_RGB2BGR))
            except Exception as e:
                return render(request, 'result.html', {'result': f'❌ PDF conversion failed: {e}'})
        else:
            img = cv2.imread(file_path)
            if img is None:
                try:
                    p = Image.open(file_path)
                    images.append(cv2.cvtColor(np.array(p), cv2.COLOR_RGB2BGR))
                except Exception as e:
                    return render(request, 'result.html', {'result': f'❌ Unable to read uploaded file: {e}'})
            else:
                images.append(img)

        full_text = ""
        raw_pages = []

        # ✅ OCR for each image
        for i, img in enumerate(images):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape
            max_dim = 2000
            if max(h, w) > max_dim:
                scale = max_dim / max(h, w)
                gray = cv2.resize(gray, (int(w * scale), int(h * scale)))

            gray = cv2.bilateralFilter(gray, 9, 75, 75)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            try:
                text = pytesseract.image_to_string(thresh, lang='eng')
            except Exception:
                text = pytesseract.image_to_string(thresh)

            text = clean_text(text)
            print("🔍 OCR Extracted (first 200 chars):", text[:200])
            raw_pages.append(text)
            full_text += f"\n--- Page {i + 1} ---\n" + text + "\n"

        # ✅ Extract values
        glucose = find_value('glucose', full_text) or find_value('sugar', full_text)
        bp = find_value('blood pressure', full_text) or find_value('bp', full_text)
        skin = find_value('skin', full_text) or find_value('skin thickness', full_text)
        insulin = find_value('insulin', full_text)
        bmi = find_value('bmi', full_text)
        preg = find_value('preg', full_text) or find_value('pregnancies', full_text)
        pedigree = find_value('pedigree', full_text) or find_value('diabetes pedigree', full_text)
        age = find_age(full_text)  # ✅ fixed version

        extracted = {
            'Glucose': glucose if glucose is not None else 'Not found',
            'Blood Pressure': bp if bp is not None else 'Not found',
            'Skin Thickness': skin if skin is not None else 'Not found',
            'Insulin': insulin if insulin is not None else 'Not found',
            'BMI': bmi if bmi is not None else 'Not found',
            'Pregnancies': preg if preg is not None else 'Not found',
            'Diabetes Pedigree': pedigree if pedigree is not None else 'Not found',
            'Age': age if age is not None else 'Not found',
        }

        def num_or_zero(x):
            return float(x) if (x is not None and str(x) != 'Not found') else 0.0

        try:
            lg()
            pred = predict_for_input(
                num_or_zero(glucose),
                num_or_zero(bp),
                num_or_zero(skin),
                num_or_zero(insulin),
                num_or_zero(bmi),
                num_or_zero(preg),
                num_or_zero(pedigree),
                num_or_zero(age)
            )
            pred = int(pred[0]) if isinstance(pred, (list, tuple)) else int(pred)
        except Exception as e:
            return render(request, 'result.html', {'result': f'Prediction failed: {e}'})

        map_url = None
        if pred == 1:
            try:
                ip_info = requests.get("https://ipinfo.io/json", timeout=3).json()
                city = ip_info.get('city', '')
                if city:
                    map_url = f"https://www.google.com/maps/search/diabetes+doctor+near+{city}"
                else:
                    map_url = "https://www.google.com/maps/search/diabetes+doctor+near+me"
            except Exception:
                map_url = "https://www.google.com/maps/search/diabetes+doctor+near+me"

        highlighted_text = full_text
        highlight_keys = ['glucose', 'sugar', 'blood pressure', 'bp', 'insulin', 'bmi', 'preg', 'pregnancies', 'age', 'skin', 'pedigree']
        for key in highlight_keys:
            try:
                highlighted_text = re.sub(
                    rf"({key}[^\n\r]{{0,30}}([0-9]+(?:\.[0-9]+)?))",
                    r"<mark>\1</mark>",
                    highlighted_text,
                    flags=re.IGNORECASE
                )
            except:
                pass

        msg = "⚠️ Possible Diabetes detected based on uploaded report." if pred == 1 else "✅ No Diabetes indication found in report."

        return render(request, 'result.html', {
            'result': msg,
            'extracted': extracted,
            'map_url': map_url,
            'scanned_text': highlighted_text,
            'raw_pages': raw_pages
        })

    return redirect('predict')
