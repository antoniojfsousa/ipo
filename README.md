# ipo

## Proposta de Desenvolvimento de Sistema Inteligente de Gestão Clínica NF-IPO Lisboa

### Visão Geral

O objetivo é substituir o atual modelo de gestão baseado em múltiplos ficheiros Excel por um **Ecossistema de Dados Unificado**. Este sistema deve ser capaz de centralizar a jornada do doente com Neurofibromatose tipo 1, garantindo que a informação flua de forma automática, sequencial e segura.

### Estrutura de Dados Integrada

O sistema deve fundir as três fontes de informação atuais num único perfil por doente:

- **Dados Demográficos e Clínicos Base:** (Antiga Base Geral).
- **Decisões Multidisciplinares:** Integração direta das propostas de tratamento do GMNF (eliminando a duplicação de dados).
- **Monitorização Terapêutica:** Registo sequencial de tratamentos específicos, como os inibidores MEK.

### Proposta de Solução

O sistema deve ter um **módulo de verificação de Consentimento Informado**. A extração de dados só é ativada após a validação ética (doente/tutores).

**Atualização Autónoma** através de utilização de técnicas de Data Mining e NLP (Processamento de Linguagem Natural) para atualizar o histórico do doente a partir de notas de consulta e relatórios hospitalares.

**Sistema de Alarmística e Segurança** permitindo que a base de dados atue como um sentinela clínico, disparando alertas para:

- Perda de seguimento
- Controlo de exames (alerta para exames solicitados mas não realizados, ou exames periódicos em atraso segundo o protocolo)
- Triagem automática de relatórios de exames (imagiologia/patologia) que detetem resultados críticos, sinalizando o doente para avaliação prioritária

### Interoperabilidade

Para a viabilização deste projeto, solicitamos o foco nos seguintes pontos:

- Ligação aos sistemas SClínico e bases de dados centrais do IPO.
- Configuração de janelas temporais e critérios de urgência para a alarmística.
- Um painel de controlo onde o médico ou o enfermeiro valide as sugestões do sistema, em vez de inserir dados manualmente.
- Visualização cronológica de todos os eventos (Consultas > GMNF > Exames > Terapêutica).

### Impacto Esperado

- Libertação da equipa médica de tarefas de dactilografia e gestão de ficheiros Excel.
- Garantia de que nenhum doente perde o seguimento ou exames críticos por falha administrativa.
- Base de dados estruturada, fidedigna e pronta para investigação clínica de alto nível.
