INSERT INTO
	ICATU.CLIENT_IA_TB (CLIENT_ID, CLIENT_NM, CLIENT_ABREV)
VALUES
	(1, 'Open AI', 'openai'),
	(2, 'Anthropic', 'anthropic'),
	(3, 'Groq', 'groq'),
	(4, 'Gemini', 'google-gla');

VACUUM
ANALYZE ICATU.CLIENT_IA_TB;

INSERT INTO
	ICATU.CLIENT_MODEL_TB (CLIENT_ID, MODEL_NM, DESCRICAO, CUSTO, ORDENACAO)
VALUES
	(
		1,
		'gpt-4.1-mini',
		'Modelo acessível que equilibra velocidade e inteligência',
		'Input: $0.40 / 1M tokens; Cached input: $0.10 / 1M tokens; Output: $1.60 / 1M tokens',
		2
	),
	(
		1,
		'gpt-4.1',
		'Modelo mais inteligente para tarefas complexas',
		'Input: $2.00 / 1M tokens; Cached input: $0.50 / 1M tokens; Output: $8.00 / 1M tokens',
		3
	),
	(
		1,
		'gpt-4.1-nano',
		'Modelo mais rápido e custo-efetivo para tarefas de baixa latência',
		'Input: $0.100 / 1M tokens; Cached input: $0.025 / 1M tokens; Output: $0.400 / 1M tokens',
		1
	),
	(
		2,
		'claude-sonnet-4-20250514',
		'Equilíbrio ideal entre inteligência, custo e velocidade',
		'Input: $3 / 1M tokens; Cached input: $0.30 / 1M tokens; Output: $15 / 1M tokens',
		2
	),
	(
		2,
		'claude-opus-4-20250514',
		'Modelo mais inteligente para tarefas complexas',
		'Input: $15 / 1M tokens; Cached input: $1.50 / 1M tokens; Output: $75 / 1M tokens',
		3
	),
	(
		2,
		'claude-3-5-haiku-20241022',
		'Modelo mais rápido e custo-efetivo',
		'Input: $0.80 / 1M tokens; Cached input: $0.08 / 1M tokens; Output: $4 / 1M tokens',
		1
	),
	(3, 'llama-3.3-70b-versatile', NULL, NULL, 1),
	(
		4,
		'gemini-2.5-flash',
		'Modelo híbrido com 1 milhão de tokens de contexto e orçamentos de pensamento',
		'Input: $0.30 / 1M tokens (texto/imagem/vídeo); Output: $2.50 / 1M tokens; Context caching: $0.075 / 1M tokens (texto/imagem/vídeo) ou $0.25 / 1M tokens (áudio)',
		2
	),
	(
		4,
		'gemini-2.5-pro',
		'Modelo multiuso avançado para programação e raciocínio complex',
		'Input: $1.25 / 1M tokens; Output: $10.00 / 1M tokens; Context caching: $0.31 / 1M tokens (comandos ≤ 200 mil tokens) ou $0.625 / 1M tokens (comandos > 200 mil tokens)',
		3
	),
	(
		4,
		'gemini-2.0-flash-lite',
		'Modelo econômico e de alto desempenho para uso em larga escala',
		'Input: $0.075 / 1M tokens; Output: $0.30 / 1M tokens',
		1
	);

VACUUM
ANALYZE ICATU.CLIENT_MODEL_TB;