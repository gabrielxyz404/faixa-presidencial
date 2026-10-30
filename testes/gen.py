import json,sys,re
sys.stdout.reconfigure(encoding='utf-8')
S=sys.argv[1]
r=json.load(open(S+'/raw.json',encoding='utf-8'))
G={
1:('C','PL ordinária correta; reconhece Lei 15.270/2025 (isenção até R$5 mil) e calcula só o degrau adicional; LRF 14 citada. Nota: IRPF sem anterioridade/noventena flag é correto.'),
2:('C','Reconhece EC 141/2026 como já promulgada, trata como ato de comunicação redundante (art. 7º, XIII). Excelente.'),
3:('P','Instrumento PEC e art. 7º XIII corretos, cita EC 141 na base; mas o objeto é lido como "fim da escala 6x1" (ignora 36h) e o parecer não diz que 36h < 40h da EC.'),
4:('C','Lei complementar (art. 7º I + ADCT 10 II, art. 69, 257/41) exata; o instrumento sai rotulado "Projeto de Lei · lei complementar".'),
5:('P','PL e LRF 16/17 ok; mas lê como "reajuste das aposentadorias" e usa R$15 bi padrão (14º real custa ~R$70-90 bi); não cita art. 195 §5º.'),
6:('C','Inconstitucional: art. 5º XLVII + 60 §4º IV; "nem PEC pode". (Exceção de guerra declarada, art. 84 XIX, não mencionada.)'),
7:('C','PEC, art. 228, "controverso" por cláusula pétrea contestada: leitura fiel do debate doutrinário.'),
8:('C','Inconstitucional, art. 60 §4º I-III, crime de responsabilidade (Lei 1.079/50). Correto.'),
9:('W','Base jurídica cita arts. 136-141 e exige autorização do Congresso, mas o motor classifica como decreto "sem Congresso", CONSTITUCIONAL, "reforço da segurança" R$1,6 bi; ignora art. 137 (autorização prévia) e que para o Rio o cabível seria estado de defesa/GLO.'),
10:('C','PLP, art. 153 VII, art. 69, anterioridade+noventena (150 III b,c) e vigência só em 2028. Receita R$0,1 bi discutível, mas coerente.'),
11:('P','Decreto correto (IPI é extrafiscal, art. 153 §1º), LRF 14 ok; mas lê "fim do IPI" inteiro (R$70 bi) em vez de só carros elétricos (poucos bi).'),
12:('P','PL e quórum simples plausíveis; receita one-off R$232 bi coerente com valor de mercado; falta art. 37 XIX/177 e Lei 13.303; "melhora o primário em R$75 bi" mistura receita única com primário.'),
13:('C','MP cabível, LRF 16/17 sinalizada, custo R$30 bi coerente (+18% sobre R$170 bi). Aviso de que MP caduca em 4 meses (art. 62 §3º) também correto.'),
14:('P','Ato do Executivo sem custo e sem alerta de preço livre/Lei 13.303 art. 8º ou art. 173; só flag de mercado. Congelar preço sem custo fiscal está subestimado.'),
15:('C','PL, "controverso" e judicialização certa por art. 128 CP e ADPF 54; fiel ao STF.'),
16:('P','PL ordinário plausível (real PLP 12/2024 foi complementar); não parseia o valor/hora nem cita Tema 1291/vínculo; sem base jurídica.'),
17:('W','Não reconhece a LC 179/2021 (autonomia e mandato fixo já existem); trata como "ato político vago", sem base jurídica. Contraste com 6x1, que foi reconhecido.'),
18:('P','PL (lei autorizativa art. 37 XIX) é o instrumento certo, mas o motor lê como reestatização/desapropriação (art. 5º XXIV) em vez de art. 20 IX/176/173; R$30 bi inventado; "controverso" pelo motivo errado.'),
19:('C','Inconstitucional por art. 37 XV (irredutibilidade). Poupa R$21 bi (folha real maior) e rotula "reajuste", mas veredito/artigo corretos.'),
20:('P','PEC e art. 201 §7º corretos; mas o sinal fiscal está invertido: "melhora o primário em R$24 bi" quando reduzir idade mínima eleva gasto.'),
21:('P','Ato do Executivo e constitucional plausíveis (Lei 11.473/2007); não exige pedido do governador nem cita o decreto/portaria; custo padrão R$5 bi e escopo "nacional" para um estado.'),
22:('P','PL e anterioridade (art. 150 III b) ok; ignora que a Lei 15.270/2025 já criou retenção de 10% sobre dividendos (reconhecera a lei no caso 1); R$30 bi é padrão.'),
23:('C','PEC 308/49, art. 14 §5º e 82, e anterioridade eleitoral do art. 16 citadas. Correto.'),
24:('C','PL ordinário correto (art. 7º XIX + ADCT 10 §1º, ADO 20); custo R$1,3 bi modesto mas ok. Sem base jurídica exibida.'),
25:('C','PEC por art. 206 IV (gratuidade), correto; receita R$6 bi tem sinal de "perda" no texto mas é ordem de grandeza aceitável.'),
}
def cl(x):
    L=[l for l in x['txt'].split('\n') if l.strip()]
    def after(k):
        return L[L.index(k)+1] if k in L and L.index(k)+1<len(L) else '-'
    head=L[1]
    j=[k for k,l in enumerate(L) if l.startswith('Controle de constit')][0]
    ver=L[j].split(': ',1)[-1]; why=L[j+1]
    i=[k for k,l in enumerate(L) if l.startswith('Ocultar base') or l.startswith('Ver base')]
    base=' / '.join(b.split(' · ')[0] for b in L[i[0]+1:j]) if i else '-'
    warn=[L[k+1] for k,l in enumerate(L) if l=='!']
    res=after('RESUMO DO ANALISTA')
    def names(a,b):
        if a not in L: return []
        s=L.index(a); e=L.index(b) if b in L else len(L)
        return [L[k-1] for k in range(s,e) if L[k].startswith('●') and k>s]
    gan=names('Quem ganha','Quem perde')
    s=L.index('Quem perde') if 'Quem perde' in L else None
    per=[]
    if s:
        e=min([k for k,l in enumerate(L) if l=='Riscos' and k>s]+[len(L)])
        per=[L[k-1] for k in range(s,e) if L[k].startswith('●')]
    m=re.search(r'(\d+) ganham · (\d+) perdem',x['txt'])
    ap=re.findall(r'Se a medida for aprovada: ([^\n]*)',x['txt'])
    coer=re.search(r'Coerência com o seu partido\n([^\n]*)',x['txt'])
    via=after('Viabilidade')
    risk=re.search(r'\nRiscos\n([^\n]*)',x['txt'])
    return dict(head=head,custo=after('CUSTO ANUAL'),rec=after('RECEITA ANUAL'),uni=after('ÚNICO / EXTRA'),tram=after('TRAMITAÇÃO'),res=res,ver=ver,why=why,base=base,warn=warn,gan=gan[:4],per=per[:4],gp=m.group(0) if m else '-',via=via,coer=coer.group(1) if coer else '-',risk=risk.group(1) if risk else '-',ap=ap)
out=['# Resultado: sondagem do motor de politicas (Faixa Presidencial)\n','Cada proposta foi digitada em #caixa, "Assinar e enviar", e o parecer lido do modal (nao consumiu acao: "Desistir" devolve). Julgamento: C=correto, P=parcial, W=errado, contra a legislacao brasileira real.\n']
out.append('| # | Proposta | Instrumento | Tramitacao | Veredito CF / artigos | Custo/Receita/Unico | Efeitos (ganha / perde, risco) | Avisos | Nota | Motivo |')
out.append('|---|---|---|---|---|---|---|---|---|---|')
cnt={'C':0,'P':0,'W':0}
for x in r:
    d=cl(x); g,why=G[x['i']]; cnt[g]+=1
    cr=f"custo {d['custo']}; receita {d['rec']}; unico {d['uni']}"
    ef=f"{d['gp']}. Ganha: {', '.join(d['gan']) or '-'}. Perde: {', '.join(d['per']) or '-'}. Maior risco: {d['risk']}. Viabilidade {d['via']}. {d['coer']}"
    out.append(f"| {x['i']} | {x['t']} | {d['head']} | {d['tram']} | {d['ver']}: {d['why'][:220]} Arts./base: {d['base'][:200]} | {cr} | {ef} | {' ; '.join(d['warn'])[:300] or '-'} | {g} | {why} |".replace('\n',' '))
out.append(f"\n**Placar: {cnt['C']} corretos, {cnt['P']} parciais, {cnt['W']} errados (de 25).**\n")
out.append('## Efeitos pos-aprovacao (3 casos)\n')
out.append(open(S+'/pos.md',encoding='utf-8').read())
open(S+'/resultado.md','w',encoding='utf-8').write('\n'.join(out))
print(cnt)
