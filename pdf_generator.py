from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO
import json
from datetime import datetime

def generate_pdf(article):
    """Generate a PDF for an article"""
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#003366'),
        spaceAfter=12
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#003366'),
        spaceAfter=8,
        spaceBefore=12
    )
    
    normal_style = styles['Normal']
    
    # Title
    story.append(Paragraph(article.title, title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Metadata
    metadata = f"<b>Author:</b> {article.author or 'Unknown'}<br/>"
    metadata += f"<b>Published:</b> {article.published_date.strftime('%Y-%m-%d %H:%M') if article.published_date else 'N/A'}<br/>"
    metadata += f"<b>URL:</b> <link href='{article.url}'>{article.url}</link><br/>"
    metadata += f"<b>Primary Topic:</b> {article.primary_topic}"
    story.append(Paragraph(metadata, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Topic Scores
    story.append(Paragraph("Topic Relevance Scores", heading_style))
    try:
        topic_scores = json.loads(article.topic_scores)
        score_data = [['Topic', 'Score']]
        for topic, score in sorted(topic_scores.items(), key=lambda x: x[1], reverse=True):
            score_data.append([topic, str(score)])
        
        score_table = Table(score_data, colWidths=[3*inch, 1*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(score_table)
    except:
        story.append(Paragraph("No topic scores available", normal_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # AI Summary
    story.append(Paragraph("AI-Generated Summary", heading_style))
    summary_text = article.summary or "No summary available"
    story.append(Paragraph(summary_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Full Content
    story.append(Paragraph("Full Article Content", heading_style))
    content_text = article.content or "No content available"
    # Split long content into paragraphs
    paragraphs = content_text.split('\n')
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para, normal_style))
            story.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
