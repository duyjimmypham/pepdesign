# Using PepDesign in Colab (Before GitHub Push)

Since you haven't pushed to GitHub yet, here's how to use your local code in Colab.

---

## Quick Fix: Modify Cell 1

In the Colab notebook, **replace Cell 1** with this:

```python
# Upload your local pepdesign folder
print("📤 Upload your pepdesign.zip file")
print("(Create zip: Right-click PepDesign folder → Send to → Compressed folder)\n")

from google.colab import files
uploaded = files.upload()

# Extract
import zipfile
zip_name = list(uploaded.keys())[0]
with zipfile.ZipFile(zip_name, 'r') as zip_ref:
    zip_ref.extractall('/content/')

# Navigate to pepdesign
%cd /content/PepDesign/pepdesign

# Install dependencies
!pip install -q pydantic biopython pandas pandarallel pdbfixer openmm

print("\n✅ PepDesign installed from local files")
```

---

## Step-by-Step Instructions

### 1. Create ZIP of Your Code

**Windows:**

1. Navigate to `e:\Fifa\Projects\PeptideDesign\`
2. Right-click the `PepDesign` folder
3. Select **Send to → Compressed (zipped) folder**
4. Rename to `pepdesign.zip` if needed

### 2. Upload Notebook to Colab

1. Go to https://colab.research.google.com/
2. **File → Upload notebook**
3. Select `PepDesign_Colab.ipynb`

### 3. Modify Cell 1

- Delete the existing Cell 1 content
- Copy/paste the code from "Quick Fix" above

### 4. Run the Notebook

1. **Runtime → Change runtime type → GPU (T4)**
2. Run Cell 1 → It will prompt you to upload
3. Upload `pepdesign.zip` you created
4. Continue running remaining cells

---

## After You Push to GitHub

Once you've pushed your code, you can revert Cell 1 to the simple version:

```python
# Clone from GitHub
!git clone https://github.com/duyjimmypham/pepdesign.git
%cd pepdesign
!pip install -q pydantic biopython pandas pandarallel pdbfixer openmm
```

---

## Alternative: Google Drive Method

If ZIP upload is slow, use Google Drive:

### 1. Upload to Drive

1. Upload `PepDesign` folder to Google Drive

### 2. Mount Drive in Colab

```python
from google.colab import drive
drive.mount('/content/drive')

# Copy from Drive
!cp -r /content/drive/MyDrive/PepDesign /content/
%cd /content/PepDesign/pepdesign

# Install dependencies
!pip install -q pydantic biopython pandas pandarallel pdbfixer openmm
```

---

## Summary

**Before GitHub push**: Use ZIP upload or Google Drive  
**After GitHub push**: Use `git clone`

Both methods give you **real ProteinMPNN** - the only difference is how the code gets to Colab!
