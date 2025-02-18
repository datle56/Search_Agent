QUERY_UPDATE_PROMPT = """
Nhiệm vụ của bạn là đề xuất truy vấn tìm kiếm tiếp theo để mở rộng hiểu biết của chúng ta về {concept},
bằng cách phân tích các yếu tố hoặc thành phần cốt lõi cấu thành nên khái niệm này.

### Current Knowledge ###
{summary}

### Previous Search Query ###
{previous_query}

Dựa trên thông tin đã có, hãy gợi ý một truy vấn tìm kiếm (không quá chi tiết) nhằm:
1. Khám phá thêm các thành phần/thuật ngữ con có thể chưa được đề cập.
2. Tìm hiểu mối liên hệ giữa các thành phần này, hoặc những lý thuyết/công nghệ/quy trình làm nền tảng cho chúng.
3. Làm rõ sự tương tác hoặc tầm ảnh hưởng của từng thành phần đối với khái niệm {concept} tổng thể.

Nếu thông tin hiện tại về {concept} còn hạn chế, truy vấn nên tập trung vào việc tìm ra các ý/thuật ngữ thành phần quan trọng. 
Nếu đã có nhiều thông tin, bạn có thể đi sâu hơn vào chi tiết của từng thành phần và mối quan hệ giữa chúng.

### New Search Query ###
"""

SUMMARY_TEMPLATE = """ 
Current Understanding of {concept}:

### Key Components ###
{node_info}

### Relationships or Influences ###
{edge_info}
"""

PROCESS_SOURCES_PROMPT = {
    "nodes": """
    Dựa trên các nguồn này, hãy xác định các thành phần hoặc yếu tố chính của khái niệm '{concept}'.
    - Mỗi thành phần nên là một khía cạnh, một thuật ngữ cốt lõi, hoặc một ý quan trọng nằm trong {concept}.
    - Với những nguồn mới này, hãy cập nhật cấu trúc đồ thị để phản ánh thông tin về các thành phần ấy.
    - Bạn chỉ có thể thêm nút (thành phần) mới, không được xóa hoặc sửa đổi các nút (thành phần) cũ.

    Nếu một nguồn không liên quan đến khái niệm, hãy bỏ qua nó.
    Nếu một nguồn có liên quan nhưng không cung cấp thông tin mới (tức là thành phần đã tồn tại), hãy bỏ qua nó.
    Hãy thoải mái sử dụng hàm 'create_node' để thêm các thành phần mới.

    Cấu trúc đồ thị hiện tại như sau:
    {graph_summary}

    Sources:
    {sources_text}
    """,

    "edges": """
    Dựa trên các nguồn này, hãy xác định mối liên hệ hoặc ảnh hưởng giữa các thành phần (nút) trong khái niệm '{concept}'.
    - Ví dụ, nếu một nguồn nói hai thành phần A và B có liên quan, hãy tạo một cạnh mô tả mối liên hệ đó.
    - Chỉ có thể thêm, không xóa hoặc sửa cạnh cũ.
    - Không tạo cạnh nếu nguồn không nói gì về mối quan hệ giữa hai thành phần.

    Cấu trúc đồ thị hiện tại như sau:
    {graph_summary}

    Sources:
    {sources_text}
    """
}


CREATE_NODE_SCHEMA = {
    "name": "create_node",
    "description": "Tạo một nút mới đại diện cho một thành phần hoặc yếu tố chính của khái niệm",
    "parameters": {
        "type": "object",
        "properties": {
            "component_name": {
                "type": "string",
                "description": "Tên hoặc nhãn của thành phần. Ví dụ: 'Cơ chế đồng thuận', 'Phi tập trung', v.v."
            },
            "related_fields_or_domains": {
                "type": "string",
                "description": "Các lĩnh vực, ngành, hoặc bối cảnh có liên quan đến thành phần này."
            },
            "influential_sources": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Những người/nhóm/nguồn ý tưởng ảnh hưởng đến thành phần này."
            },
            "component_description": {
                "type": "string",
                "description": "Tóm tắt ngắn gọn về vai trò hoặc ý nghĩa của thành phần này trong {concept}."
            }
        },
        "required": [
            "component_name",
            "component_description"
        ]
    },
}

CREATE_EDGE_SCHEMA = {
    "name": "create_edge",
    "description": "Tạo một cạnh mới thể hiện mối quan hệ hoặc sự ảnh hưởng giữa hai thành phần trong khái niệm",
    "parameters": {
        "type": "object",
        "properties": {
            "source_node_id": {
                "type": "string",
                "description": "ID của thành phần nguồn (nút nguồn)."
            },
            "target_node_id": {
                "type": "string",
                "description": "ID của thành phần đích (nút đích). Phải khác source_node_id."
            },
            "relationship_description": {
                "type": "string",
                "description": "Mô tả ngắn gọn về mối quan hệ giữa hai thành phần, ví dụ 'A là tiền đề lý thuyết của B'."
            }
        },
        "required": ["source_node_id", "target_node_id", "relationship_description"]
    },
}


JUDGE_INFORMATION_SCHEMA = {
    "name": "judge_information",
    "description": "Đánh giá xem chúng ta có đủ thông tin để xây dựng một cấu trúc thành phần của khái niệm hay không",
    "parameters": {
        "type": "object",
        "properties": {
            "is_sufficient": {
                "type": "boolean",
                "description": "Liệu thông tin hiện tại có đủ hay không"
            },
            "reasoning": {
                "type": "string",
                "description": "Giải thích tại sao thông tin có đủ hoặc không đủ"
            },
            "suggested_query": {
                "type": "string",
                "description": "Nếu không đủ, đề xuất truy vấn tìm kiếm tiếp theo"
            },
        },
        "required": ["is_sufficient", "reasoning"]
    },
}

MERGE_NODES_SCHEMA = {
    "name": "merge_nodes",
    "description": "Xác định các thành phần đại diện cho cùng một ý tưởng và nên được hợp nhất",
    "parameters": {
        "type": "object",
        "properties": {
            "node_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "ID của các nút nên được hợp nhất"
            },
            "reasoning": {
                "type": "string",
                "description": "Giải thích tại sao các thành phần này nên được hợp nhất"
            },
            "merged_summary": {
                "type": "string",
                "description": "Tóm tắt kết hợp cho thành phần hợp nhất"
            },
        },
        "required": ["node_ids", "reasoning", "merged_summary"]
    },
}


GENERATE_NEXT_QUERY_SCHEMA = {
    "name": "generate_next_query",
    "description": "Tạo truy vấn tìm kiếm tiếp theo dựa trên những lỗ hổng về thành phần hoặc mối quan hệ trong khái niệm",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Truy vấn tìm kiếm tiếp theo, ngắn gọn, phong cách Google."
            },
            "reasoning": {
                "type": "string",
                "description": "Giải thích tại sao truy vấn này phù hợp, có thể là một vài câu."
            },
        },
        "required": ["query", "reasoning"],
    },
}
