# Azure Document Intelligence Demo

A professional Streamlit application that demonstrates Azure Document Intelligence capabilities for extracting structured data from documents.

## Features

- **Smart Document Analysis**: Extract key-value pairs, tables, and text using Azure's prebuilt-document model
- **Interactive UI**: Clean, professional interface suitable for manager demonstrations
- **Side-by-Side View**: Compare original documents with extracted data
- **Multiple Export Formats**: Download results as JSON or Excel files
- **Confidence Scoring**: View confidence levels for all extracted elements
- **Multi-Format Support**: PDF, PNG, JPG, JPEG, BMP, TIFF

## Prerequisites

- Python 3.8 or higher
- Azure Document Intelligence service
- Azure subscription

## Setup Instructions

### 1. Get Azure Document Intelligence Credentials

1. **Create Azure Document Intelligence Resource**:
   - Go to [Azure Portal](https://portal.azure.com)
   - Click "Create a resource" → Search "Document Intelligence"
   - Select "Document Intelligence" and click "Create"
   - Choose your subscription, resource group, and region
   - Select pricing tier (F0 for free tier, S0 for standard)
   - Click "Review + create" → "Create"

2. **Get Your Credentials**:
   - Navigate to your Document Intelligence resource
   - Go to "Keys and Endpoint" in the left menu
   - Copy the **Endpoint** and **Key 1**

### 2. Install Dependencies

```bash
# Clone or download this project
cd azure-document-intelligence-demo

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Set your Azure credentials as environment variables:

**Windows (Command Prompt)**:
```cmd
set AZURE_DI_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/
set AZURE_DI_KEY=your-api-key-here
```

**Windows (PowerShell)**:
```powershell
$env:AZURE_DI_ENDPOINT="https://your-resource-name.cognitiveservices.azure.com/"
$env:AZURE_DI_KEY="your-api-key-here"
```

**macOS/Linux**:
```bash
export AZURE_DI_ENDPOINT="https://your-resource-name.cognitiveservices.azure.com/"
export AZURE_DI_KEY="your-api-key-here"
```

**Alternative: Create .env file**:
```bash
# Create .env file in project root
echo "AZURE_DI_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/" > .env
echo "AZURE_DI_KEY=your-api-key-here" >> .env
```

### 4. Additional Dependencies (PDF Support)

For PDF processing, you may need to install `poppler`:

**macOS**:
```bash
brew install poppler
```

**Ubuntu/Debian**:
```bash
sudo apt-get install poppler-utils
```

**Windows**:
- Download poppler from [poppler for Windows](https://blog.alivate.com.au/poppler-windows/)
- Add poppler/bin to your PATH

## Running the Demo

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## How to Use

1. **Upload Document**: Use the sidebar to upload a PDF or image file
2. **Analyze**: Click "Analyze Document" to process with Azure Document Intelligence
3. **Review Results**: Explore extracted data in the tabbed interface:
   - **Key-Value Pairs**: Structured data with confidence scores
   - **Tables**: Extracted tables with original structure
   - **Text Content**: Line-by-line text with confidence levels
   - **Confidence Details**: Overall confidence statistics
4. **Export**: Download results as JSON or Excel files

## Project Structure

```
azure-document-intelligence-demo/
├── app.py                 # Main Streamlit application
├── document_processor.py  # Azure Document Intelligence logic
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## File Descriptions

- **`app.py`**: Main Streamlit application with UI components and user interaction logic
- **`document_processor.py`**: Core Azure Document Intelligence processing, data extraction, and export functionality
- **`config.py`**: Environment variable management and configuration validation

## Supported Document Types

The application works best with:
- **Forms and Invoices**: Business documents with structured fields
- **Contracts and Agreements**: Legal documents with key terms
- **Reports and Certificates**: Formatted documents with tables and data
- **Receipts and Statements**: Financial documents with line items

## Demo Tips

- **Image Quality**: Use high-resolution, well-lit images for best results
- **File Size**: Keep files under 50MB for optimal performance
- **Language**: Works best with English documents
- **Format**: PDF files can be multi-page; images should be single-page

## Troubleshooting

### Common Issues

1. **"Azure Document Intelligence not configured!"**
   - Verify environment variables are set correctly
   - Check that your Azure resource is active and accessible

2. **"Document processing failed"**
   - Ensure file is not corrupted and in supported format
   - Check Azure resource has remaining quota
   - Verify network connectivity to Azure

3. **PDF preview not working**
   - Install poppler utilities for your operating system
   - Ensure PDF is not password-protected

4. **Low confidence scores**
   - Try higher resolution images
   - Ensure text is clearly visible and not skewed
   - Consider using PDF format instead of images

### Getting Help

- Check Azure Document Intelligence [documentation](https://docs.microsoft.com/en-us/azure/applied-ai-services/form-recognizer/)
- Review Azure service status and quotas in Azure Portal
- Ensure all dependencies are correctly installed

## Cost Considerations

- **Free Tier (F0)**: 500 pages per month
- **Standard Tier (S0)**: Pay per page analyzed
- Monitor usage in Azure Portal to avoid unexpected charges

## Security Notes

- Never commit API keys to version control
- Use environment variables or Azure Key Vault for credentials
- Consider network security for production deployments

## License

This is a demonstration project. Please review Azure Document Intelligence pricing and terms of service for production use.