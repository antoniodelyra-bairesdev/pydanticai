export type TipoExecucao = {
    id: number
    nome: string
}

export type DadosExecucao = {
    id: number
    identificador_titulo: string
    identificador_documento_cobranca: string
    vencimento: string
    valor: number
    percentual_juros_mora_ao_mes: number
    percentual_sobre_valor_multa_mora: number
    conteudo_arquivo_remessa: string | null
    arquivo_id_boleto_parcial_pdf: string | null
    conteudo_arquivo_retorno: string | null
    arquivo_id_boleto_completo_pdf: string | null
    contrato_id: number
    execucao_daycoval_id: number
}

export type PassoExecucao = {
    id: number
    nome: string
    inicio: string
    fim: string | null
    erro: string | null
    execucao_daycoval_id: number
}

export type Execucao = {
    id: number;
    tipo_execucao: TipoExecucao;
    inicio: string;
    fim: string | null;
    erro: string | null;
    usuario: {
        id: number;
        email: string;
        nome: string;
    };
    passos: PassoExecucao[],
    dados: DadosExecucao[]
};