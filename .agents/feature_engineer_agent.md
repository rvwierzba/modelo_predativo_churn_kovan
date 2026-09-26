# Agente Engenheiro de Features (Feature Engineer Agent)

## Escopo & Responsabilidades
O **Agente Engenheiro de Features** é responsável por extrair variáveis preditivas de alta relevância técnica e temporal para antecipar a erosão silenciosa de receita no relacionamento B2B.

## Principais Atributos Desenvolvidos
- **Tendência de Receita (`variacao_receita_obs`)**: Mede a velocidade e inclinação de receita entre o início e o fim da janela de observação.
- **Mix de Portfólio (`pct_servicos`, `pct_hardware`, `foco_em_servicos`)**: Quantifica a proporção de receita em serviços recorrentes vs hardware corporativo.
- **Amplitude de SKUs (`total_skus`, `num_marcas`)**: Identifica o estreitamento de mix de produtos.
- **Engajamento Comercial (`contatos_realizados_obs`, `dias_sem_contato_medio_obs`)**: Identifica lacunas na cobertura comercial e queda na cadência do Account Manager.
- **Conversão de Pipeline (`taxa_conversao_pipeline`)**: Razão entre oportunidades ganhas e abertas no CRM.
