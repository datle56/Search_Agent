QUERY_UPDATE_PROMPT = """
Nhiệm vụ của bạn là đề xuất truy vấn tìm kiếm tiếp theo để mở rộng hiểu biết của chúng ta về {concept},
bằng cách phân tích các thành phần hoặc khía cạnh cốt lõi cấu thành nên khái niệm này.

### Current Knowledge ###
{summary}

### Previous Search Query ###
{previous_query}

Dựa trên thông tin này, hãy tạo một truy vấn tìm kiếm (không quá chi tiết) để giúp chúng ta:
1. Khám phá thêm những thành phần/ý tưởng phụ còn chưa đề cập
2. Tìm hiểu mối quan hệ hoặc ảnh hưởng giữa các thành phần này
3. Hiểu rõ hơn vai trò từng thành phần đối với khái niệm tổng thể

Nếu thông tin về {concept} còn hạn chế, hãy nhắm đến việc tìm các thành phần quan trọng. 
Nếu đã có nhiều thông tin, bạn có thể đề xuất truy vấn đi sâu hơn vào chi tiết và mối quan hệ giữa chúng.

### New Search Query ###
"""

SUMMARY_TEMPLATE = """ 
Current Understanding of {concept}:

### Key Components ###
{node_info}

### Relationships ###
{edge_info}
"""

PROCESS_SOURCES_PROMPT = {
    "nodes": """
    Dựa trên các nguồn này, hãy xác định các thành phần hoặc khái niệm con cốt lõi liên quan đến '{concept}'.
    Tạo một nút (node) cho mỗi thành phần riêng biệt. 
    Cấu trúc đồ thị hiện tại như sau:
    {graph_summary}

    Với những nguồn mới này, hãy cập nhật cấu trúc đồ thị để phản ánh thông tin mới. 
    Bạn chỉ có thể thêm nút, không thể xóa hoặc sửa đổi các nút hiện có.
    Nếu một nguồn không liên quan đến khái niệm, hãy bỏ qua nó. 
    Nếu một nguồn có liên quan nhưng không cung cấp thông tin mới (tức là nút đã tồn tại), hãy bỏ qua nó.
    Tuy nhiên, bạn nên rất thoải mái trong việc sử dụng hàm 'create_node'.

    Sources:
    {sources_text}
    """,

    "edges": """
    ### Phải trả lời bằng tiếng việt###
    Dựa trên các nguồn này, hãy xác định các mối quan hệ hoặc ảnh hưởng giữa các nút (thành phần) trong khái niệm '{concept}'.
    Tạo các cạnh (edge) để kết nối những thành phần có liên quan. 
    Cấu trúc đồ thị hiện tại như sau:
    {graph_summary}

    Với những nguồn mới này, hãy cập nhật cấu trúc đồ thị để phản ánh thông tin mới. 
    Bạn chỉ có thể thêm cạnh, không thể xóa hoặc sửa đổi các cạnh hiện có. 
    Ví dụ, nếu có hai nút A và B, và một nguồn chỉ ra rằng A và B có liên quan, bạn nên tạo một cạnh giữa chúng. 
    Nếu bạn biết A và B có liên quan nhưng nguồn không đề cập trực tiếp, bạn vẫn có thể tạo một cạnh giữa chúng nếu hợp lý.

    Hãy đảm bảo rằng ID của nút là chính xác. 
    Không sử dụng cùng một ID nút cho cả nguồn và đích (tránh vòng lặp tự thân).

    Bạn không bắt buộc phải thêm cạnh mới! 
    Nếu chỉ có một nút, đừng thêm cạnh. 
    Chỉ thêm cạnh nếu có một kết nối có ý nghĩa giữa hai nút riêng biệt. 
    Nếu đã có một cạnh giữa hai nút, đừng thêm cạnh mới giữa chúng!

    Nếu một nguồn không liên quan đến khái niệm, hãy bỏ qua nó. 
    Nếu một nguồn có liên quan nhưng không cung cấp thông tin mới (tức là cạnh đã tồn tại), hãy bỏ qua nó.

    Sources:
    {sources_text}
    """
}
