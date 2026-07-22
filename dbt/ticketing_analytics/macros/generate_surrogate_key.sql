{% macro generate_surrogate_key(columns) -%}
md5({%- for col in columns -%}coalesce(cast({{ col }} as varchar), '_null_'){%- if not loop.last %} || '|' || {% endif -%}{%- endfor -%})
{%- endmacro %}
