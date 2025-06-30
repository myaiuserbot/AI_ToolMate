SELECT tool_name, use_case, affiliate_link, affiliate_amount
FROM `your_project_id.AI_ToolMate_Tools.All_AI_Tool_Data`
WHERE category LIKE '%{category}%' AND affiliate_link IS NOT NULL
ORDER BY CAST(affiliate_amount AS FLOAT64) DESC
LIMIT 3;
