"""
Azure Document Intelligence processing logic
"""
import json
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError
import streamlit as st


class DocumentProcessor:
    """Handler for Azure Document Intelligence operations"""

    def __init__(self, endpoint: str, key: str):
        """Initialize the Document Intelligence client"""
        try:
            self.client = DocumentAnalysisClient(
                endpoint=endpoint,
                credential=AzureKeyCredential(key)
            )
        except Exception as e:
            raise Exception(f"Failed to initialize Azure Document Intelligence client: {str(e)}")

    def analyze_document(self, document_bytes: bytes) -> Dict[str, Any]:
        """
        Analyze document using Azure Document Intelligence prebuilt-document model

        Args:
            document_bytes: Document content as bytes

        Returns:
            Dict containing extracted data and metadata
        """
        try:
            # Use prebuilt-document model for general document analysis
            poller = self.client.begin_analyze_document(
                "prebuilt-document",
                document_bytes
            )
            result = poller.result()

            # Extract data
            extracted_data = {
                "key_value_pairs": self._extract_key_value_pairs(result),
                "tables": self._extract_tables(result),
                "text_content": self._extract_text(result),
                "pages": len(result.pages),
                "confidence_summary": self._calculate_confidence_summary(result)
            }

            return extracted_data

        except AzureError as e:
            raise Exception(f"Azure Document Intelligence analysis failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Document analysis failed: {str(e)}")

    def _extract_key_value_pairs(self, result) -> List[Dict[str, Any]]:
        """Extract key-value pairs with confidence scores"""
        key_value_pairs = []

        for kv_pair in result.key_value_pairs:
            if kv_pair.key and kv_pair.value:
                key_confidence = 0
                value_confidence = 0

                # Safely extract key confidence
                if hasattr(kv_pair.key, 'confidence') and kv_pair.key.confidence is not None:
                    key_confidence = round(kv_pair.key.confidence, 3)

                # Safely extract value confidence
                if hasattr(kv_pair.value, 'confidence') and kv_pair.value.confidence is not None:
                    value_confidence = round(kv_pair.value.confidence, 3)

                key_value_pairs.append({
                    "key": kv_pair.key.content,
                    "value": kv_pair.value.content,
                    "key_confidence": key_confidence,
                    "value_confidence": value_confidence
                })

        return key_value_pairs

    def _extract_tables(self, result) -> List[Dict[str, Any]]:
        """Extract tables with structure and confidence scores"""
        tables = []

        for table_idx, table in enumerate(result.tables):
            # Safely extract table confidence
            table_confidence = 0
            if hasattr(table, 'confidence') and table.confidence is not None:
                table_confidence = round(table.confidence, 3)

            table_data = {
                "table_id": table_idx + 1,
                "row_count": table.row_count,
                "column_count": table.column_count,
                "cells": [],
                "confidence": table_confidence
            }

            for cell in table.cells:
                # Safely extract cell confidence
                cell_confidence = 0
                if hasattr(cell, 'confidence') and cell.confidence is not None:
                    cell_confidence = round(cell.confidence, 3)

                table_data["cells"].append({
                    "content": cell.content,
                    "row_index": cell.row_index,
                    "column_index": cell.column_index,
                    "confidence": cell_confidence
                })

            tables.append(table_data)

        return tables

    def _extract_text(self, result) -> Dict[str, Any]:
        """Extract text content with confidence"""
        text_data = {
            "content": result.content,
            "pages": []
        }

        for page in result.pages:
            page_data = {
                "page_number": page.page_number,
                "width": page.width,
                "height": page.height,
                "unit": page.unit,
                "lines": []
            }

            for line in page.lines:
                # Safely extract line confidence
                line_confidence = 0
                if hasattr(line, 'confidence') and line.confidence is not None:
                    line_confidence = round(line.confidence, 3)

                page_data["lines"].append({
                    "content": line.content,
                    "confidence": line_confidence
                })

            text_data["pages"].append(page_data)

        return text_data

    def _calculate_confidence_summary(self, result) -> Dict[str, float]:
        """Calculate overall confidence statistics"""
        all_confidences = []

        # Collect confidences from key-value pairs
        for kv_pair in result.key_value_pairs:
            if kv_pair.key and hasattr(kv_pair.key, 'confidence') and kv_pair.key.confidence is not None:
                all_confidences.append(kv_pair.key.confidence)
            if kv_pair.value and hasattr(kv_pair.value, 'confidence') and kv_pair.value.confidence is not None:
                all_confidences.append(kv_pair.value.confidence)

        # Collect confidences from tables
        for table in result.tables:
            if hasattr(table, 'confidence') and table.confidence is not None:
                all_confidences.append(table.confidence)
            for cell in table.cells:
                if hasattr(cell, 'confidence') and cell.confidence is not None:
                    all_confidences.append(cell.confidence)

        # Collect confidences from text lines
        for page in result.pages:
            for line in page.lines:
                if hasattr(line, 'confidence') and line.confidence is not None:
                    all_confidences.append(line.confidence)

        if all_confidences:
            return {
                "average": round(sum(all_confidences) / len(all_confidences), 3),
                "minimum": round(min(all_confidences), 3),
                "maximum": round(max(all_confidences), 3),
                "count": len(all_confidences)
            }
        else:
            return {"average": 0, "minimum": 0, "maximum": 0, "count": 0}

    def export_to_json(self, data: Dict[str, Any]) -> str:
        """Export extracted data to JSON format"""
        return json.dumps(data, indent=2, ensure_ascii=False)

    def export_to_excel(self, data: Dict[str, Any]) -> Tuple[bytes, Dict[str, pd.DataFrame]]:
        """
        Export extracted data to Excel format

        Returns:
            Tuple of (Excel bytes, DataFrames dict)
        """
        dfs = {}

        # Key-Value Pairs sheet
        if data.get("key_value_pairs"):
            dfs["Key_Value_Pairs"] = pd.DataFrame(data["key_value_pairs"])

        # Tables sheets
        for i, table in enumerate(data.get("tables", [])):
            # Create table structure
            if table["cells"]:
                # Create a matrix for the table
                table_matrix = []
                max_row = max(cell["row_index"] for cell in table["cells"]) + 1
                max_col = max(cell["column_index"] for cell in table["cells"]) + 1

                # Initialize matrix with empty strings
                matrix = [["" for _ in range(max_col)] for _ in range(max_row)]

                # Fill matrix with cell content
                for cell in table["cells"]:
                    matrix[cell["row_index"]][cell["column_index"]] = cell["content"]

                dfs[f"Table_{i+1}"] = pd.DataFrame(matrix)

        # Text content sheet
        if data.get("text_content", {}).get("pages"):
            text_lines = []
            for page in data["text_content"]["pages"]:
                for line in page["lines"]:
                    text_lines.append({
                        "page": page["page_number"],
                        "content": line["content"],
                        "confidence": line["confidence"]
                    })
            if text_lines:
                dfs["Text_Lines"] = pd.DataFrame(text_lines)

        # Confidence Summary sheet
        if data.get("confidence_summary"):
            confidence_df = pd.DataFrame([data["confidence_summary"]])
            dfs["Confidence_Summary"] = confidence_df

        # Create Excel file in memory
        import io
        excel_buffer = io.BytesIO()

        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            for sheet_name, df in dfs.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        excel_buffer.seek(0)
        return excel_buffer.getvalue(), dfs