"""
heading_chunker.py — chiến lược chunking theo TIÊU ĐỀ/MỤC (heading/section).

Đây là file MỚI, KHÔNG sửa src/chunking.py, để 42 test có sẵn không bị ảnh hưởng.

Vì sao chunk theo heading hợp với chủ đề K3: văn bản quy định được biên soạn theo mục,
mỗi mục đã là một đơn vị ngữ nghĩa trọn vẹn (điều kiện + ngoại lệ + thời hạn nằm cùng
một chỗ). Cắt theo ký tự hay theo câu dễ tách rời "điều kiện" khỏi "ngoại lệ" của nó.

CHIẾN LƯỢC CỦA BÙI GIA HUY:
    HeadingChunker — cắt section theo heading, section dài hơn max_chunk_size
    thì dùng RecursiveChunker cắt nhỏ, nhưng KHÔNG gắn lại tiêu đề vào các mảnh con.
    Đây là thí nghiệm đối chứng: đo xem việc MẤT breadcrumb ở chunk con
    có ảnh hưởng retrieval quality không.
"""
from __future__ import annotations

import re

from .chunking import RecursiveChunker

# Dòng heading Markdown: từ 1 đến 6 dấu # ở đầu dòng, theo sau là khoảng trắng.
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)


def split_into_sections(text: str) -> list[tuple[list[str], str]]:
    """
    Tách text thành các section theo dòng heading.

    Trả về list ``(breadcrumb, section_text)``:
        breadcrumb   — list tiêu đề từ ngoài vào trong, ví dụ ["Quy chế đào tạo", "Add/drop"]
        section_text — dòng heading + toàn bộ nội dung tới trước heading kế tiếp

    Phần văn bản đứng TRƯỚC heading đầu tiên (nếu có) là một section với breadcrumb rỗng.
    """
    if not text.strip():
        return []

    sections: list[tuple[list[str], str]] = []
    current_breadcrumb: list[str] = []
    current_section_lines: list[str] = []

    for line in text.splitlines(keepends=True):
        match = HEADING_PATTERN.search(line)
        if match:
            # Lưu section hiện tại trước khi chuyển
            if current_section_lines:
                section_text = "".join(current_section_lines)
                if section_text.strip():
                    sections.append((list(current_breadcrumb), section_text))

            # Cập nhật breadcrumb theo level của heading mới
            level = len(match.group(1))  # 1-6 dấu #
            title = match.group(2).strip()

            # Cắt breadcrumb đến level hiện tại
            current_breadcrumb = current_breadcrumb[: level - 1]
            current_breadcrumb.append(title)

            # Bắt đầu section mới
            current_section_lines = [line]
        else:
            current_section_lines.append(line)

    # Lưu section cuối cùng
    if current_section_lines:
        section_text = "".join(current_section_lines)
        if section_text.strip():
            sections.append((list(current_breadcrumb), section_text))

    return sections


class HeadingChunker:
    """
    Chunk theo cấu trúc heading của Markdown. Mỗi section là một chunk;
    nếu section dài hơn max_chunk_size thì dùng RecursiveChunker cắt nhỏ.

    ĐẶC ĐIỂM QUAN TRỌNG: KHÔNG gắn lại breadcrumb/tiêu đề vào các mảnh con
    của section dài. Đây là thí nghiệm đối chứng so với HeadingRecursiveChunker.

    Tham số:
        max_chunk_size — ngưỡng độ dài (mặc định 800), vượt ngưỡng mới cắt nhỏ
        fallback — chunker dùng khi phải cắt nhỏ (mặc định RecursiveChunker)
    """

    def __init__(self, max_chunk_size: int = 800, fallback=None) -> None:
        self.max_chunk_size = max_chunk_size
        self.fallback = fallback or RecursiveChunker(chunk_size=max_chunk_size)

    def chunk(self, text: str) -> list[str]:
        """Chia text thành các chunk theo cấu trúc heading."""
        if not text.strip():
            return []

        sections = split_into_sections(text)
        result: list[str] = []

        for _, section in sections:
            if len(section) <= self.max_chunk_size:
                # Section vừa đủ, giữ nguyên
                result.append(section)
            else:
                # Section quá dài, cắt nhỏ bằng RecursiveChunker
                # LƯU Ý: KHÔNG gắn breadcrumb vào mảnh con
                sub_chunks = self.fallback.chunk(section)
                result.extend(sub_chunks)

        # Loại bỏ chunk rỗng và strip whitespace
        return [piece.strip() for piece in result if piece.strip()]


class HeadingRecursiveChunker:
    """
    Như HeadingChunker, nhưng GẮN LẠI breadcrumb tiêu đề vào từng mảnh con.

    LỚP NÀY DO NGUYỄN HUY ĐỨC PHỤ TRÁCH (không phải của Gia Huy).
    Giữ lại ở đây để tránh import lỗi nhưng KHÔNG implement.
    """

    def __init__(
        self, max_chunk_size: int = 800, fallback=None, separator: str = " > "
    ) -> None:
        self.max_chunk_size = max_chunk_size
        self.fallback = fallback or RecursiveChunker(chunk_size=max_chunk_size)
        self.separator = separator

    def _prefix(self, breadcrumb: list[str]) -> str:
        """Tiền tố breadcrumb gắn vào mỗi mảnh con."""
        if not breadcrumb:
            return ""
        return f"[{self.separator.join(breadcrumb)}]\n"

    def chunk(self, text: str) -> list[str]:
        raise NotImplementedError(
            "HeadingRecursiveChunker do Nguyen Huy Duc phu trach, "
            "khong phai cua Bui Gia Huy."
        )


SAMPLE = """# Quy chế đào tạo

Văn bản này áp dụng cho sinh viên đại học chính quy.

## Đăng ký học phần

Sinh viên đăng ký học phần theo lịch của Phòng Đào tạo.
Hạn chót drop môn là ngày làm việc thứ 15 (the 15th business day) của học kỳ.

## Rút môn

Sau hạn add/drop, việc bỏ môn được tính là rút môn (Withdrawal) và ghi điểm W.
"""


def _self_check() -> int:
    """Kiểm tra nhanh cả hai chunker mà không cần pytest."""
    failures: list[str] = []

    # 1. Kiểm tra split_into_sections
    try:
        sections = split_into_sections(SAMPLE)
        assert len(sections) >= 3, f"ky vong >= 3 section, co {len(sections)}"
        breadcrumbs = [crumb for crumb, _ in sections]
        assert any(
            len(crumb) >= 2 for crumb in breadcrumbs
        ), f"breadcrumb chua long cap: {breadcrumbs}"
        print(
            f"OK split_into_sections -> {len(sections)} section, "
            f"breadcrumb sau nhat {max(len(c) for c in breadcrumbs)} cap"
        )
    except NotImplementedError:
        failures.append("split_into_sections CHUA implement")
    except AssertionError as error:
        failures.append(f"split_into_sections SAI: {error}")

    # 2. Kiểm tra HeadingChunker
    for name, chunker in [
        ("HeadingChunker", HeadingChunker(max_chunk_size=120)),
        ("HeadingRecursiveChunker", HeadingRecursiveChunker(max_chunk_size=120)),
    ]:
        try:
            assert chunker.chunk("") == [], "text rong phai tra []"
            chunks = chunker.chunk(SAMPLE)
            assert isinstance(chunks, list) and chunks, "phai tra list khong rong"
            assert all(isinstance(piece, str) for piece in chunks), "moi phan tu phai la str"
            assert all(piece.strip() for piece in chunks), "khong duoc co chunk rong"
            print(
                f"OK {name} -> {len(chunks)} chunk, dai nhat {max(len(p) for p in chunks)} ky tu"
            )
        except NotImplementedError:
            failures.append(f"{name}.chunk CHUA implement")
        except AssertionError as error:
            failures.append(f"{name}.chunk SAI: {error}")

    # 3. Kiểm tra HeadingRecursiveChunker (phải raise NotImplementedError)
    try:
        chunks = HeadingRecursiveChunker(max_chunk_size=120).chunk(SAMPLE)
        # Nếu không raise, kiểm tra xem có breadcrumb không
        assert any(
            piece.startswith("[") and "]" in piece.split("\n")[0] for piece in chunks
        ), "khong thay mang con nao mang breadcrumb"
        print("OK HeadingRecursiveChunker co ggan breadcrumb vao mang con")
    except NotImplementedError:
        # Đây là kết quả mong đợi cho Gia Huy
        pass
    except AssertionError as error:
        failures.append(f"breadcrumb: {error}")

    if failures:
        print(f"\n--- CON {len(failures)} VIEC ---")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("\n--- heading_chunker self-check OK ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(_self_check())
