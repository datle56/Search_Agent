PROCESS_SOURCES_PROMPT = {
    "initial_node": """
    Bạn là một người học đang tìm hiểu về các thuật ngữ chuyên ngành.
    Hãy tạo ra node đầu tiên cho khái niệm '{concept}'.
    Node này cần chứa định nghĩa chính xác và rõ ràng về '{concept}', 
    nêu ra các đặc điểm cơ bản và liệt kê các thuật ngữ chủ chốt liên quan. 
    Ví dụ, nếu '{concept}' là "Transformer", định nghĩa cần đề cập đến các thành phần như "Encoder", "Decoder", "Self-Attention", v.v.
    
    Cấu trúc đồ thị hiện tại như sau:
    {graph_summary}
    
    Sources:
    {sources_text}
    """,
    "nodes": """
    Dựa trên các nguồn sau đây, hãy xác định và tạo ra các thành phần hoặc khái niệm con cốt lõi liên quan đến '{concept}'.
    Nếu bạn đang học một khái niệm như "Transformer", hãy liệt kê và tạo node cho các thuật ngữ như "Encoder", "Decoder", "Self-Attention", "Positional Encoding", v.v.
    Đồng thời, nếu từ "Encoder" xuất hiện, hãy mở rộng tìm hiểu các thành phần phụ liên quan như "Multi-Head Attention", "Feed-Forward Network",...
    
    Cấu trúc đồ thị hiện tại như sau:
    {graph_summary}
    
    Với những nguồn mới này, hãy cập nhật cấu trúc đồ thị để phản ánh thông tin bổ sung.
    Bạn chỉ được thêm node mới, không được xóa hoặc sửa đổi các node đã có.
    
    Sources:
    {sources_text}
    """,
    "edges": """
    Dựa trên các nguồn sau đây, hãy xác định mối liên hệ hoặc ảnh hưởng giữa các node (thành phần) trong khái niệm '{concept}'.
    Ví dụ, nếu một nguồn chỉ ra rằng "Encoder" và "Decoder" có mối liên hệ chặt chẽ trong kiến trúc của Transformer, hãy tạo một cạnh mô tả mối liên hệ đó.
    Hoặc nếu từ "Encoder" liên quan đến các thành phần phụ như "Multi-Head Attention", hãy tạo các cạnh mô tả mối quan hệ giữa chúng.
    
    Cấu trúc đồ thị hiện tại như sau:
    {graph_summary}
    
    Sources:
    {sources_text}
    """
}
