"""
Cover Comparison Dialog

This module provides a dialog for displaying PDF and cover images side by side
for manual verification when automatic comparison fails.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from utils.icons import get_app_icon
from i18n import tr


class CoverComparisonDialog(QDialog):
    """
    Dialog for showing side-by-side comparison of PDF first page and album cover.
    
    Used when Safe Rename detects a mismatch between the PDF content and the
    selected album cover, allowing the user to make an informed decision.
    """
    
    def __init__(self, parent=None, pdf_image_path=None, cover_image_path=None, 
                 ssim_score=0.0, threshold=0.7, file_name="", album_name=""):
        """
        Initialize the comparison dialog.
        
        Args:
            parent: Parent widget
            pdf_image_path (str): Path to the extracted PDF first page image
            cover_image_path (str): Path to the album cover image
            ssim_score (float): The calculated similarity score
            threshold (float): The threshold used for comparison
            file_name (str): Name of the file being renamed
            album_name (str): Name of the target album
        """
        super().__init__(parent)
        self.setWindowTitle(tr("messages.cover_comparison.title"))
        self.setModal(True)
        self.resize(800, 600)
        
        # Set dialog icon
        app_icon = get_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        
        self.pdf_image_path = pdf_image_path
        self.cover_image_path = cover_image_path
        self.ssim_score = ssim_score
        self.threshold = threshold
        self.file_name = file_name
        self.album_name = album_name
        
        self.user_choice = None  # Will be 'proceed', 'cancel', or None
        
        self._setup_ui()
        self._load_images()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Title and explanation
        title_label = QLabel(tr("messages.cover_comparison.mismatch_detected"))
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # File and album info
        info_layout = QVBoxLayout()
        file_label = QLabel(tr("messages.cover_comparison.file_label", file_name=self.file_name))
        album_label = QLabel(tr("messages.cover_comparison.album_label", album_name=self.album_name))
        score_label = QLabel(tr("messages.cover_comparison.similarity_score", 
                                score=f"{self.ssim_score:.3f}", 
                                threshold=f"{self.threshold:.3f}"))
        
        info_layout.addWidget(file_label)
        info_layout.addWidget(album_label)
        info_layout.addWidget(score_label)
        layout.addLayout(info_layout)
        
        # Images container
        images_frame = QFrame()
        images_frame.setFrameStyle(QFrame.Box)
        images_layout = QHBoxLayout(images_frame)
        
        # PDF image section
        pdf_section = QVBoxLayout()
        pdf_title = QLabel(tr("messages.cover_comparison.pdf_cover"))
        pdf_title.setAlignment(Qt.AlignCenter)
        pdf_title.setFont(title_font)
        pdf_section.addWidget(pdf_title)
        
        self.pdf_scroll = QScrollArea()
        self.pdf_scroll.setWidgetResizable(True)
        self.pdf_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.pdf_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.pdf_label.setStyleSheet("border: 1px solid gray;")
        self.pdf_scroll.setWidget(self.pdf_label)
        pdf_section.addWidget(self.pdf_scroll)
        
        # Album cover section
        cover_section = QVBoxLayout()
        cover_title = QLabel(tr("messages.cover_comparison.album_cover"))
        cover_title.setAlignment(Qt.AlignCenter)
        cover_title.setFont(title_font)
        cover_section.addWidget(cover_title)
        
        self.cover_scroll = QScrollArea()
        self.cover_scroll.setWidgetResizable(True)
        self.cover_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.cover_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setStyleSheet("border: 1px solid gray;")
        self.cover_scroll.setWidget(self.cover_label)
        cover_section.addWidget(self.cover_scroll)
        
        images_layout.addLayout(pdf_section)
        images_layout.addLayout(cover_section)
        layout.addWidget(images_frame)
        
        # Explanation text
        explanation = QLabel(tr("messages.cover_comparison.explanation"))
        explanation.setWordWrap(True)
        explanation.setAlignment(Qt.AlignCenter)
        layout.addWidget(explanation)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.proceed_btn = QPushButton(tr("messages.cover_comparison.proceed_anyway"))
        self.proceed_btn.clicked.connect(self._proceed_anyway)
        
        self.cancel_btn = QPushButton(tr("messages.cover_comparison.cancel_rename"))
        self.cancel_btn.clicked.connect(self._cancel_rename)
        self.cancel_btn.setDefault(True)  # Make cancel the default action
        
        button_layout.addWidget(self.proceed_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def _load_images(self):
        """Load and display the comparison images."""
        # Load PDF image
        if self.pdf_image_path:
            pdf_pixmap = QPixmap(self.pdf_image_path)
            if not pdf_pixmap.isNull():
                # Scale to fit scroll area while maintaining aspect ratio
                scaled_pdf = pdf_pixmap.scaled(
                    350, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.pdf_label.setPixmap(scaled_pdf)
            else:
                self.pdf_label.setText(tr("messages.cover_comparison.pdf_load_error"))
        else:
            self.pdf_label.setText(tr("messages.cover_comparison.pdf_not_available"))
        
        # Load cover image
        if self.cover_image_path:
            cover_pixmap = QPixmap(self.cover_image_path)
            if not cover_pixmap.isNull():
                # Scale to fit scroll area while maintaining aspect ratio
                scaled_cover = cover_pixmap.scaled(
                    350, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.cover_label.setPixmap(scaled_cover)
            else:
                self.cover_label.setText(tr("messages.cover_comparison.cover_load_error"))
        else:
            self.cover_label.setText(tr("messages.cover_comparison.cover_not_available"))
    
    def _proceed_anyway(self):
        """User chose to proceed with rename despite mismatch."""
        self.user_choice = 'proceed'
        self.accept()
    
    def _cancel_rename(self):
        """User chose to cancel the rename operation."""
        self.user_choice = 'cancel'
        self.reject()
    
    def get_user_choice(self):
        """
        Get the user's choice after dialog closes.
        
        Returns:
            str: 'proceed' if user wants to rename anyway, 'cancel' if not, None if dialog was closed
        """
        return self.user_choice
