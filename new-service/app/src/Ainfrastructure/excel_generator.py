import pandas as pd
import io
from typing import List, BinaryIO
from ..Ddomain.entities import Transaction
from ..Ddomain.repositories import ExcelGeneratorRepository


class ExcelGenerator(ExcelGeneratorRepository):
    """Implementation of Excel generator"""
    
    def generate_excel(self, transactions: List[Transaction], filename: str) -> BinaryIO:
        """Generate Excel file from transactions"""
        # Convert transactions to dictionaries
        data = [
            {
                'fecha_proceso': t.fecha_proceso,
                'fecha_consumo': t.fecha_consumo,
                'descripcion': t.descripcion,
                'tipo_operacion': t.tipo_operacion,
                'soles': t.soles,
                'dolares': t.dolares
            }
            for t in transactions
        ]
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Transactions', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Transactions']
            
            # Format headers
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            # Write headers with formatting
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Auto-adjust column widths
            for col_num, column in enumerate(df.columns):
                max_length = max(
                    df[column].astype(str).map(len).max(),
                    len(str(column))
                ) + 2
                worksheet.set_column(col_num, col_num, min(max_length, 50))
        
        excel_buffer.seek(0)
        return excel_buffer