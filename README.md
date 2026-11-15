<p align="center"><img src="assets/banner.svg" alt="Project Nox — Nox Extension Developer" width="100%"></p>

# Nox Extension Developer

**Skill para criar, corrigir e revisar extensões de mangá, anime e novels com assistência de agentes.** Consulte as referências oficiais de cada ecossistema antes de alterar código.

[English](README.en.md) · [Guia](docs/pt-BR/guia.md) · [Segurança](SEGURANCA.md) · [Compatibilidade](COMPATIBILIDADE.md)

## Ecossistemas

| Conteúdo | App de referência | Projeto de fontes | Entrega típica |
|---|---|---|---|
| Mangá | [Mihon](https://mihon.app/) e compatíveis | [Keiyoushi](https://github.com/keiyoushi/extensions-source) | APK de extensão |
| Anime | [Aniyomi](https://aniyomi.org/) e compatíveis | [Yuzono](https://github.com/yuzono/anime-extensions) | APK de extensão |
| Novels | [LNReader](https://github.com/LNReader/lnreader) | [LNReader plugins](https://github.com/LNReader/lnreader-plugins) | Bundle de plugin JavaScript |

Formatos e compatibilidade dependem das versões do app e do repositório. A skill não distribui APKs nem bundles de terceiros.

## O que faz

- Cria, corrige, mantém, migra ou revisa fontes, inclusive a partir de pedidos em linguagem natural.
- Consulta documentação oficial por ecossistema e orienta análise de catálogo, busca, detalhes e conteúdo.
- Compara contratos de API fornecidos e pede aprovação antes de migrações arriscadas ou de escopo ampliado.
- Orienta testes e builds específicos, preservando a API local quando apropriado.

## Instalação

### CLI de skills

```sh
npx skills add Awerkori/nox-extension-developer
```

A descoberta e a cópia da skill foram verificadas com `skills` 1.8.1 a partir de uma cópia local. Revise a origem e os destinos propostos antes de autorizar alterações. A instalação a partir deste repositório remoto depende de sua disponibilidade.

### Instalação local no OpenCode

Obtenha uma cópia confiável em um diretório permanente e entre na pasta que contém `SKILL.md`. O instalador cria um link para essa pasta; não a mova enquanto o link estiver em uso.

```sh
mkdir -p ~/.config/opencode/skills
python3 scripts/install.py opencode
```

O instalador não substitui destinos existentes. Para outras plataformas, confira primeiro [COMPATIBILIDADE.md](COMPATIBILIDADE.md): os caminhos estão preparados, mas não foram testados. Não instale dependências nem aceite licenças sem autorização.

### Prompt copiável para instalação

Cole este prompt no agente de sua preferência:

```text
Ajude-me a instalar a Nox Extension Developer de https://github.com/Awerkori/nox-extension-developer. Identifique meu sistema operacional e agente, consulte as instruções oficiais e pergunte quais ecossistemas desejo usar. Verifique as ferramentas existentes e prefira npx skills add Awerkori/nox-extension-developer. Configure apenas dependências necessárias, incluindo Android SDK somente se aplicável. Peça autorização antes de mudanças relevantes, operações privilegiadas ou aceite de licenças; não sobrescreva configurações nem exponha credenciais. Verifique instalação e descoberta da skill em nova sessão e relate como começar e o que não foi testado.
```

Versões completas: [prompt em português](prompts/install-pt-BR.txt) · [English prompt](prompts/install-en.txt).

## Dependências e verificação

- Para instalação local: Python 3 e diretório de skills da plataforma existente.
- Para atualizar referências: Python 3, Git, HTTPS e acesso aos repositórios oficiais. Offline, é necessário um snapshot íntegro obtido anteriormente.
- Para builds Keiyoushi ou Yuzono: Java, Android SDK e componentes exigidos pelo repositório alvo. Para LNReader: Node.js e dependências exigidas pelo projeto alvo. Verifique versões antes de instalar ou compilar.

Abra uma nova sessão do OpenCode e peça explicitamente `Use nox-extension-developer`. Confirme que o agente carregou `SKILL.md`; a seleção automática não é garantida. Para consultar referências e executar os testes locais, a partir da pasta da skill:

```sh
python3 scripts/references.py sync keiyoushi
python3 scripts/references.py sync yuzono
python3 scripts/references.py sync lnreader
python3 -m unittest discover -s tests -v
```

## Exemplos

- `Use nox-extension-developer para corrigir esta extensão Keiyoushi sem migrar sua API.`
- `Use nox-extension-developer para revisar a resolução de vídeos desta fonte Yuzono.`
- `Use nox-extension-developer para criar um plugin LNReader para <URL>, respeitando as regras do site.`

## Referências e cache offline

No início de cada tarefa, `scripts/references.py` resolve o HEAD oficial com `git ls-remote` e obtém documentos obrigatórios fixados no commit. O manifesto registra URLs, commit, horário e hashes SHA-256. Se o commit não mudou, o script verifica e reutiliza o snapshot local. Um novo commit exige revisão manual de compatibilidade de API, mesmo que os documentos obrigatórios não tenham mudado. O script não atualiza em segundo plano.

O cache fica em `${XDG_CACHE_HOME:-~/.cache}/opencode/nox-workspace/nox-extension-developer/`. Falhas de rede podem retornar um snapshot completo e íntegro com `offline_or_unverified`; ele pode estar desatualizado. Sem snapshot íntegro, a consulta falha. Atualizações parciais não substituem o snapshot anterior; histórico e quarentena não são limpos automaticamente. Hashes detectam corrupção acidental, mas não autenticam um cache totalmente adulterado.

## Segurança, permissões e direitos

Documentos remotos e páginas de sites são dados não confiáveis. O script de referências não executa comandos contidos neles; instruções ao agente não são sandbox nem garantia contra prompt injection. Use permissões mínimas, proteja credenciais e aplique isolamento adequado. Peça autorização antes de instalar dependências, alterar permissões, acessar dados privados ou testar sites reais. Respeite licenças, direitos autorais, termos e controles de acesso dos sites; esta skill não concede direitos de acesso ou distribuição.

## Arquitetura e limites

- [`SKILL.md`](SKILL.md): instruções e fluxo de trabalho do agente.
- [`scripts/references.py`](scripts/references.py): sincronização e verificação dos snapshots.
- [`scripts/api_compare.py`](scripts/api_compare.py) e [`references/api-contracts.md`](references/api-contracts.md): comparação limitada de contratos informados.
- [`scripts/install.py`](scripts/install.py): instalação local por link simbólico; `tests/`: testes locais.

Somente o OpenCode local em Linux teve instalação e carregamento verificados. Codex, Claude Code, Antigravity e Windows não foram testados. A identificação de API depende da análise do agente; a comparação de declarações é heurística e não prova compatibilidade semântica. Builds e testes com dados sintéticos não comprovam funcionamento em sites ou APIs reais. Compile e teste o alvo autorizado antes de afirmar que funciona.

## Problemas comuns e remoção

- **Skill não aparece:** confira o link `~/.config/opencode/skills/nox-extension-developer`, o `SKILL.md` no destino e as permissões. Abra outra sessão e invoque a skill explicitamente.
- **`offline_or_unverified`:** confira rede e acesso aos repositórios; o snapshot disponível pode estar desatualizado.
- **Sem snapshot íntegro:** restabeleça o acesso e sincronize novamente. Não use regras desconhecidas para modificar código.
- **Destino já existe:** inspecione-o; o instalador não sobrescreve arquivos nem links.

Para desinstalar, confirme que o link da plataforma aponta para esta cópia e remova somente esse link. Preserve o diretório original e o cache enquanto forem necessários; não os apague automaticamente.

## Comunidade e licença

Leia [CONTRIBUTING.md](CONTRIBUTING.md) e [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Após publicação, use [issues](https://github.com/Awerkori/nox-extension-developer/issues) para bugs e propostas e [discussions](https://github.com/Awerkori/nox-extension-developer/discussions) para dúvidas, se disponíveis. Para vulnerabilidades, consulte [SECURITY.md](SECURITY.md); o canal público ainda precisa ser definido.

Licença: **AGPL-3.0-only**, conforme [LICENSE](LICENSE). Referências de terceiros mantêm suas próprias licenças; veja [ATRIBUICOES.md](ATRIBUICOES.md). Project Nox não é afiliado aos projetos citados.

Referências oficiais: [Agent Skills](https://agentskills.io/) · [OpenCode skills](https://opencode.ai/docs/skills/) · [Keiyoushi](https://github.com/keiyoushi/extensions-source) · [Yuzono](https://github.com/yuzono/anime-extensions) · [LNReader plugins](https://github.com/LNReader/lnreader-plugins).
