"""
heading_chunker.py — chiến lược chunking theo TIÊU ĐỀ/MỤC (heading/section).

Đây là file MỚI, KHÔNG sửa src/chunking.py, để 42 test có sẵn không bị ảnh hưởng.

Vì sao chunk theo heading hợp với chủ đề K3: văn bản quy định được biên soạn theo mục,
mỗi mục đã là một đơn vị ngữ nghĩa trọn vẹn (điều kiện + ngoại lệ + thời hạn nằm cùng
một chỗ). Cắt theo ký tự hay theo câu dễ tách rời "điều kiện" khỏi "ngoại lệ" của nó.

HAI LỚP DƯỚI ĐÂY LÀ MỘT CẶP THÍ NGHIỆM — khác nhau ĐÚNG MỘT BIẾN:

    HeadingChunker          (Bùi Gia Huy)    — cắt section dài, KHÔNG gắn lại tiêu đề
    HeadingRecursiveChunker (Nguyễn Huy Đức) — cắt section dài, CÓ gắn lại breadcrumb tiêu đề

Nhờ chỉ khác một biến, chênh lệch kết quả benchmark giữa hai người quy được về một
nguyên nhân duy nhất: mảnh thứ hai trở đi của một section dài có mất ngữ cảnh tiêu đề
hay không. Đây là nội dung có giá trị nhất cho phần "So sánh giữa các thành viên".

Tự kiểm tra (không cần pytest):
    py -m src.heading_chunker
"""
from __future__ import annotations

import re

from .chunking import RecursiveChunker

# Dòng heading Markdown: từ 1 đến 6 dấu # ở đầu dòng, theo sau là khoảng trắng.
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)


def split_into_sections(text: str) -> list[tuple[list[str], str]]:
    """Tách text thành các section theo dòng heading.

    Trả về list ``(breadcrumb, section_text)``:
        breadcrumb   — list tiêu đề từ ngoài vào trong, ví dụ ["Quy chế đào tạo", "Add/drop"]
        section_text — dòng heading + toàn bộ nội dung tới trước heading kế tiếp

    Phần văn bản đứng TRƯỚC heading đầu tiên (nếu có) là một section với breadcrumb rỗng.

    TODO (Huy): implement.
      1. Duyệt từng dòng của text.
      2. Dòng khớp HEADING_PATTERN -> đóng section đang mở, mở section mới.
         Cập nhật ngăn xếp breadcrumb theo cấp heading (len của nhóm '#'):
         cắt ngăn xếp về (cấp - 1) phần tử rồi append tiêu đề mới.
      3. Dòng thường -> nối vào section đang mở.
      4. Bỏ qua section rỗng sau khi strip().
    """
    raise NotImplementedError("Implement split_into_sections")


class HeadingChunker:
    """Mỗi section là một chunk; section dài hơn max_chunk_size thì hạ xuống recursive.

    Tham số:
        max_chunk_size — ngưỡng độ dài, vượt ngưỡng mới cắt nhỏ
        fallback       — chunker dùng khi phải cắt nhỏ (mặc định RecursiveChunker)
    """

    def __init__(self, max_chunk_size: int = 800, fallback=None) -> None:
        self.max_chunk_size = max_chunk_size
        self.fallback = fallback or RecursiveChunker(chunk_size=max_chunk_size)

    def chunk(self, text: str) -> list[str]:
        """
        TODO (Huy): implement.
          1. text rỗng -> trả [].
          2. sections = split_into_sections(text)
          3. Với mỗi section:
                - len(section) <= max_chunk_size  -> giữ nguyên làm 1 chunk
                - dài hơn                          -> self.fallback.chunk(section)
          4. strip từng chunk, bỏ chunk rỗng, trả list[str].

        Lưu ý: KHÔNG gắn lại tiêu đề vào các mảnh con — đó là điểm khác biệt có chủ đích
        so với HeadingRecursiveChunker. Đừng "sửa" chỗ này, vì cả thí nghiệm nằm ở đây.
        """
        raise NotImplementedError("Implement HeadingChunker.chunk")


class HeadingRecursiveChunker:
    """Như HeadingChunker, nhưng GẮN LẠI breadcrumb tiêu đề vào từng mảnh con.

    Ví dụ một section dài bị cắt làm 3 mảnh, mỗi mảnh sẽ bắt đầu bằng:

        [Quy chế đào tạo > Đăng ký học phần và thời hạn add/drop]
        <nội dung mảnh>

    Nhờ vậy mảnh thứ hai trở đi vẫn mang ngữ cảnh tiêu đề khi được embed, thay vì trở
    thành một đoạn trôi nổi không biết thuộc mục nào.
    """

    def __init__(self, max_chunk_size: int = 800, fallback=None, separator: str = " > ") -> None:
        self.max_chunk_size = max_chunk_size
        self.fallback = fallback or RecursiveChunker(chunk_size=max_chunk_size)
        self.separator = separator

    def _prefix(self, breadcrumb: list[str]) -> str:
        """Tiền tố ngữ cảnh gắn vào mỗi mảnh con. Breadcrumb rỗng -> không tiền tố."""
        if not breadcrumb:
            return ""
        return f"[{self.separator.join(breadcrumb)}]\n"

    def chunk(self, text: str) -> list[str]:
        """
        TODO (Đức): implement.
          1. text rỗng -> trả [].
          2. sections = split_into_sections(text)
          3. Với mỗi (breadcrumb, section):
                - vừa kích thước -> giữ nguyên 1 chunk
                - quá dài        -> cắt bằng self.fallback, rồi GẮN self._prefix(breadcrumb)
                                    vào ĐẦU MỌI MẢNH TỪ THỨ HAI TRỞ ĐI
                                    (mảnh đầu đã tự chứa dòng heading rồi)
          4. strip từng chunk, bỏ chunk rỗng, trả list[str].

        Đo được gì: tiền tố làm chunk dài thêm vài chục ký tự nhưng thêm tín hiệu chủ đề
        vào embedding. Ghi lại trong report: nó giúp ở query nào, và có làm chunk nhiễu
        cùng section bị đẩy lên top-3 không.
        """
        raise NotImplementedError("Implement HeadingRecursiveChunker.chunk")


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
    failures = []

    try:
        sections = split_into_sections(SAMPLE)
        assert len(sections) >= 3, f"kỳ vọng >= 3 section, có {len(sections)}"
        breadcrumbs = [crumb for crumb, _ in sections]
        assert any(len(crumb) >= 2 for crumb in breadcrumbs), f"breadcrumb chưa lồng cấp: {breadcrumbs}"
        print(f"OK  split_into_sections -> {len(sections)} section, breadcrumb sâu nhất {max(len(c) for c in breadcrumbs)} cấp")
    except NotImplementedError:
        failures.append("split_into_sections CHƯA implement")
    except AssertionError as error:
        failures.append(f"split_into_sections SAI: {error}")

    for name, chunker in [
        ("HeadingChunker", HeadingChunker(max_chunk_size=120)),
        ("HeadingRecursiveChunker", HeadingRecursiveChunker(max_chunk_size=120)),
    ]:
        try:
            assert chunker.chunk("") == [], "text rỗng phải trả []"
            chunks = chunker.chunk(SAMPLE)
            assert isinstance(chunks, list) and chunks, "phải trả list không rỗng"
            assert all(isinstance(piece, str) for piece in chunks), "mọi phần tử phải là str"
            assert all(piece.strip() for piece in chunks), "không được có chunk rỗng"
            print(f"OK  {name} -> {len(chunks)} chunk, dài nhất {max(len(p) for p in chunks)} ký tự")
        except NotImplementedError:
            failures.append(f"{name}.chunk CHƯA implement")
        except AssertionError as error:
            failures.append(f"{name}.chunk SAI: {error}")

    try:
        chunks = HeadingRecursiveChunker(max_chunk_size=120).chunk(SAMPLE)
        assert any(piece.startswith("[") and "]" in piece.split("\n")[0] for piece in chunks), (
            "không thấy mảnh con nào mang breadcrumb — hạ max_chunk_size hoặc kiểm lại việc gắn tiền tố"
        )
        print("OK  HeadingRecursiveChunker có gắn breadcrumb vào mảnh con")
    except NotImplementedError:
        pass
    except AssertionError as error:
        failures.append(f"breadcrumb: {error}")

    if failures:
        print(f"\n--- CÒN {len(failures)} VIỆC ---")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("\n--- heading_chunker self-check OK ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(_self_check())
