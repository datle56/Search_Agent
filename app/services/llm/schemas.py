# QUERY UPDATE PROMPT
QUERY_UPDATE_PROMPT = """
Tôi là một người đang học hỏi về các thuật ngữ và đang tìm kiếm các định nghĩa cụ thể cho các thuật ngữ đó.
Nhiệm vụ của bạn là đề xuất truy vấn tìm kiếm tiếp theo để mở rộng hiểu biết của chúng ta về {concept}.
Trước hết, hãy đảm bảo rằng chúng ta đã có định nghĩa cơ bản và rõ ràng về {concept} từ các kết quả tìm kiếm ban đầu.
Sau đó, dựa trên thông tin hiện có, hãy phân tích và liệt kê các thuật ngữ cốt lõi cấu thành nên khái niệm này.

### Current Knowledge ###
{summary}

### Previous Search Query ###
{previous_query}

Dựa trên thông tin đã có, hãy gợi ý một truy vấn tìm kiếm (không quá chi tiết) nhằm:
1. Khám phá thêm các thành phần con hoặc thuật ngữ con có thể chưa được đề cập.
2. Tìm hiểu mối liên hệ giữa các thành phần này, hoặc những lý thuyết/công nghệ/quy trình làm nền tảng cho chúng.
3. Làm rõ sự tương tác hoặc tầm ảnh hưởng của từng thành phần đối với khái niệm {concept} tổng thể.

Nếu thông tin hiện tại về {concept} còn hạn chế, truy vấn nên tập trung vào việc tìm ra các ý/thuật ngữ thành phần quan trọng.
Nếu đã có nhiều thông tin, bạn có thể đi sâu hơn vào chi tiết của từng thành phần và mối quan hệ giữa chúng.

### New Search Query ###
"""

# SUMMARY TEMPLATE
SUMMARY_TEMPLATE = """ 
Current Understanding of {concept}:

### Key Components ###
{node_info}

### Relationships or Influences ###
{edge_info}
"""

# PROCESS SOURCES PROMPT
PROCESS_SOURCES_PROMPT = {
    "initial_node": """
    Bạn là một người học đang tìm hiểu các thuật ngữ chuyên ngành.
    Dựa trên các nguồn sau đây, hãy tạo ra node đầu tiên cho khái niệm '{concept}'.
    Node này phải chứa định nghĩa rõ ràng về {concept} cũng như nêu ra các đặc điểm, thành phần hoặc kiến trúc chủ yếu của nó.
    Ví dụ: nếu {concept} là "Transformer", node cần định nghĩa Transformer và liệt kê các thành phần như "Encoder", "Decoder", "Self-Attention", v.v.

    Cấu trúc đồ thị hiện tại:
    {graph_summary}

    Sources:
    {sources_text}
    """,
    "nodes": """
    Dựa trên các nguồn sau đây, hãy xác định và tạo ra các thành phần hoặc thuật ngữ con liên quan đến khái niệm '{concept}'.
    - Mỗi thành phần nên là một khía cạnh, một thuật ngữ cốt lõi, hoặc một ý quan trọng nằm trong {concept}.
    - Nếu đây là lần tìm kiếm đầu tiên, hãy đảm bảo rằng node đầu tiên đã chứa định nghĩa cơ bản về {concept} trước khi mở rộng các thành phần khác.
    - Với những nguồn mới này, hãy cập nhật cấu trúc đồ thị để bổ sung thêm thông tin về các thành phần đó.
    - Bạn chỉ được thêm node mới, không được xóa hoặc thay đổi các node đã có.

    Nếu một nguồn không liên quan hoặc không cung cấp thông tin mới, hãy bỏ qua.

    Cấu trúc đồ thị hiện tại:
    {graph_summary}

    Sources:
    {sources_text}
    """,
    "edges": """
    Dựa trên các nguồn sau đây, hãy xác định mối liên hệ hoặc ảnh hưởng giữa các thành phần (node) trong khái niệm '{concept}'.
    - Nếu nguồn cho biết rằng hai thành phần có liên quan, hãy tạo một cạnh mô tả mối liên hệ đó.
    - Chỉ được thêm cạnh mới, không được xóa hoặc chỉnh sửa các cạnh đã có.
    - Không tạo cạnh nếu nguồn không nói rõ về mối liên hệ giữa các thành phần.

    Cấu trúc đồ thị hiện tại:
    {graph_summary}

    Sources:
    {sources_text}
    """
}

# CREATE NODE SCHEMA
CREATE_NODE_SCHEMA = {
    "name": "create_node",
    "description": (
        "Tạo một node mới đại diện cho một thành phần hoặc yếu tố chính của khái niệm. "
        "Đối với node đầu tiên, phần mô tả cần chứa định nghĩa cơ bản và các đặc điểm chủ đạo của {concept}."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Tên hoặc nhãn của thành phần. Ví dụ: 'Encoder', 'Self-Attention', v.v."
            },
            "origin": {
                "type": "string",
                "description": "Các lĩnh vực, ngành, hoặc bối cảnh liên quan đến thành phần này."
            },
            "influential_sources": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Danh sách những nguồn hoặc nhóm ý tưởng ảnh hưởng đến thành phần này."
            },
            "description": {
                "type": "string",
                "description": "Tóm tắt ngắn gọn về vai trò, ý nghĩa hoặc định nghĩa của thành phần này trong {concept}."
            }
        },
        "required": ["name", "description"]
    },
}

# CREATE EDGE SCHEMA
CREATE_EDGE_SCHEMA = {
    "name": "create_edge",
    "description": (
        "Tạo một cạnh mới thể hiện mối quan hệ hoặc sự ảnh hưởng giữa hai thành phần trong khái niệm."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "source_node_id": {
                "type": "string",
                "description": "ID của thành phần nguồn (node nguồn)."
            },
            "target_node_id": {
                "type": "string",
                "description": "ID của thành phần đích (node đích). Phải khác node nguồn."
            },
            "change_description": {
                "type": "string",
                "description": "Mô tả ngắn gọn về mối liên hệ, ví dụ: 'Encoder hỗ trợ xử lý song song cho Decoder'."
            }
        },
        "required": ["source_node_id", "target_node_id", "change_description"]
    },
}

# JUDGE INFORMATION SCHEMA
JUDGE_INFORMATION_SCHEMA = {
    "name": "judge_information",
    "description": (
        "Đánh giá xem thông tin hiện có đã đủ để xây dựng cấu trúc thành phần của khái niệm hay chưa."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "is_sufficient": {
                "type": "boolean",
                "description": "Cho biết thông tin hiện tại có đủ hay không."
            },
            "reasoning": {
                "type": "string",
                "description": "Giải thích tại sao thông tin hiện có lại đủ hoặc không đủ."
            },
            "suggested_query": {
                "type": "string",
                "description": "Nếu thông tin không đủ, đề xuất một truy vấn tìm kiếm tiếp theo."
            },
        },
        "required": ["is_sufficient", "reasoning"]
    },
}

# MERGE NODES SCHEMA
MERGE_NODES_SCHEMA = {
    "name": "merge_nodes",
    "description": (
        "Các ý tưởng mở rộng hoàn toàn giống nhau cần được gộp lại. "
        "Lưu ý: Các node gốc (kết quả từ lần tìm kiếm đầu tiên) sẽ không được hợp nhất. "
        "Chỉ hợp nhất các node mở rộng nếu nội dung chúng bị trùng lặp. "
        "Ví dụ: khi tìm 'Transformer', nếu kết quả có các node 'Encoder' và 'Decoder' mang nội dung khác nhau, chúng không được hợp nhất."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "node_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Danh sách các ID của node cần được hợp nhất."
            },
            "reasoning": {
                "type": "string",
                "description": "Giải thích lý do tại sao các node này nên được hợp nhất."
            },
            "merged_summary": {
                "type": "string",
                "description": "Tóm tắt kết hợp cho node sau khi hợp nhất."
            },
        },
        "required": ["node_ids", "reasoning", "merged_summary"]
    },
}

# GENERATE NEXT QUERY SCHEMA
GENERATE_NEXT_QUERY_SCHEMA = {
    "name": "generate_next_query",
    "description": (
        "Tạo truy vấn tìm kiếm tiếp theo dựa trên những khoảng trống về thành phần hoặc mối quan hệ trong khái niệm. "
        "Truy vấn cần ngắn gọn, theo phong cách tìm kiếm Google và tập trung vào việc bổ sung các thông tin còn thiếu."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Truy vấn tìm kiếm tiếp theo, ngắn gọn và súc tích."
            },
            "reasoning": {
                "type": "string",
                "description": "Giải thích tại sao truy vấn này phù hợp và cần thiết."
            },
        },
        "required": ["query", "reasoning"],
    },
}
