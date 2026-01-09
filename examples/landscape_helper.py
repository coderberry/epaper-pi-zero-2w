"""
Landscape mode helper for e-paper display.
Provides centered text rendering in landscape orientation (250x122 pixels).
"""

from epd_helper import EPDCanvas, load_font
from epd_gui import ROTATE_90


class LandscapeEPDCanvas(EPDCanvas):
    """
    E-paper canvas in landscape mode (250 wide x 122 tall).
    Provides text rendering with automatic word-wrapping and centering.
    """

    def __init__(self):
        """Initialize canvas in landscape mode."""
        super().__init__()

        # Set rotation to 90 degrees for landscape mode
        # This changes logical dimensions from 122x250 to 250x122
        self.gui.rotate = ROTATE_90

        # Update dimensions in both this class AND the gui class
        # (gui.w/gui.h are used for boundary checks in set_pixel)
        self.width = 250
        self.height = 122
        self.gui.w = 250
        self.gui.h = 122

    def render_text(self, text, font_size=24, align_h='center', align_v='middle',
                    margin=10, line_spacing=1.2, max_lines=8, font_name=None):
        """
        Render text with flexible horizontal and vertical alignment.

        Args:
            text: Text to display (empty text will be ignored)
            font_size: Font size in points (default: 24)
            align_h: Horizontal alignment - 'left', 'center', 'right' (default: 'center')
            align_v: Vertical alignment - 'top', 'middle', 'bottom' (default: 'middle')
            margin: Margin in pixels (default: 10)
            line_spacing: Line spacing multiplier (default: 1.2)
            max_lines: Maximum number of lines before truncating (default: 8)
            font_name: Font name from FONT_REGISTRY (default: None, uses default font)

        Returns:
            dict: Metadata about the rendering:
                - lines: Number of lines rendered
                - truncated: Whether text was truncated
                - text_height: Total height of text block
        """
        # Validate alignment parameters
        if align_h not in ('left', 'center', 'right'):
            align_h = 'center'
        if align_v not in ('top', 'middle', 'bottom'):
            align_v = 'middle'

        # Handle empty text
        if not text or not text.strip():
            return {"lines": 0, "truncated": False, "text_height": 0}

        # Load font
        font = load_font(font_size, font_name)

        # Calculate available width for text
        available_width = self.width - (2 * margin)

        # Split text into wrapped lines
        wrapped_lines = self._wrap_text(text, font, available_width)

        # Check if truncation is needed
        truncated = False
        if len(wrapped_lines) > max_lines:
            wrapped_lines = wrapped_lines[:max_lines]
            # Add ellipsis to last line if truncated
            last_line = wrapped_lines[-1]
            while True:
                test_line = last_line + "..."
                try:
                    bbox = font.getbbox(test_line)
                    line_width = bbox[2] - bbox[0]
                except AttributeError:
                    line_width, _ = font.getsize(test_line)

                if line_width <= available_width:
                    wrapped_lines[-1] = test_line
                    break

                # Remove last word and try again
                words = last_line.split()
                if len(words) <= 1:
                    # Single word too long, just add ellipsis
                    wrapped_lines[-1] = last_line[:max(0, len(last_line) - 3)] + "..."
                    break
                last_line = ' '.join(words[:-1])

            truncated = True

        # Calculate line height
        try:
            bbox = font.getbbox("Ay")  # Use chars with ascenders/descenders
            line_height = int((bbox[3] - bbox[1]) * line_spacing)
        except AttributeError:
            _, text_height = font.getsize("Ay")
            line_height = int(text_height * line_spacing)

        # Calculate total text block height
        total_text_height = len(wrapped_lines) * line_height

        # Calculate vertical offset based on alignment
        if align_v == 'top':
            v_offset = margin
        elif align_v == 'bottom':
            v_offset = self.height - total_text_height - margin
        else:  # middle
            v_offset = (self.height - total_text_height) // 2

        # Render each line with horizontal alignment
        for i, line in enumerate(wrapped_lines):
            # Measure line width
            try:
                bbox = font.getbbox(line)
                line_width = bbox[2] - bbox[0]
            except AttributeError:
                line_width, _ = font.getsize(line)

            # Calculate horizontal offset based on alignment
            if align_h == 'left':
                h_offset = margin
            elif align_h == 'right':
                h_offset = self.width - line_width - margin
            else:  # center
                h_offset = (self.width - line_width) // 2

            # Calculate y position for this line
            y_pos = v_offset + (i * line_height)

            # Draw the text
            self.text(h_offset, y_pos, line, font=font)

        return {
            "lines": len(wrapped_lines),
            "truncated": truncated,
            "text_height": total_text_height
        }

    def render_centered_text(self, text, font_size=24, margin=10, line_spacing=1.2,
                             max_lines=8, font_name=None):
        """
        Render text centered both horizontally and vertically with word wrapping.

        This is a convenience wrapper around render_text() for backward compatibility.

        Args:
            text: Text to display (empty text will be ignored)
            font_size: Font size in points (default: 24)
            margin: Margin in pixels on left/right (default: 10)
            line_spacing: Line spacing multiplier (default: 1.2)
            max_lines: Maximum number of lines before truncating (default: 8)
            font_name: Font name from FONT_REGISTRY (default: None, uses default font)

        Returns:
            dict: Metadata about the rendering:
                - lines: Number of lines rendered
                - truncated: Whether text was truncated
                - text_height: Total height of text block
        """
        return self.render_text(text, font_size, 'center', 'middle',
                               margin, line_spacing, max_lines, font_name)

    def _wrap_text(self, text, font, max_width):
        """
        Wrap text to fit within max_width using a greedy word-wrapping algorithm.

        Args:
            text: Text to wrap
            font: PIL ImageFont object
            max_width: Maximum width in pixels

        Returns:
            list: List of wrapped lines
        """
        lines = []

        # Split by existing newlines first
        paragraphs = text.split('\n')

        for paragraph in paragraphs:
            if not paragraph.strip():
                # Empty paragraph, add blank line
                lines.append("")
                continue

            # Split paragraph into words
            words = paragraph.split()

            if not words:
                continue

            current_line = ""

            for word in words:
                # Try adding this word to current line
                test_line = current_line + (" " if current_line else "") + word

                # Measure the width of the test line
                try:
                    bbox = font.getbbox(test_line)
                    test_width = bbox[2] - bbox[0]
                except AttributeError:
                    test_width, _ = font.getsize(test_line)

                if test_width <= max_width:
                    # Word fits, add it to current line
                    current_line = test_line
                else:
                    # Word doesn't fit
                    if current_line:
                        # Save current line and start new one
                        lines.append(current_line)
                        current_line = word
                    else:
                        # Single word is too long, add it anyway (will be truncated if needed)
                        current_line = word

                        # Check if we need to truncate this long word
                        try:
                            bbox = font.getbbox(word)
                            word_width = bbox[2] - bbox[0]
                        except AttributeError:
                            word_width, _ = font.getsize(word)

                        if word_width > max_width:
                            # Truncate word with ellipsis
                            while len(current_line) > 3:
                                current_line = current_line[:-1]
                                test = current_line + "..."
                                try:
                                    bbox = font.getbbox(test)
                                    test_width = bbox[2] - bbox[0]
                                except AttributeError:
                                    test_width, _ = font.getsize(test)
                                if test_width <= max_width:
                                    current_line = test
                                    break

            # Add the last line of this paragraph
            if current_line:
                lines.append(current_line)

        return lines
