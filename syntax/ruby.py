"""Ruby (RubyMine / org.jetbrains.plugins.ruby): Ruby, RDoc, ERB.

VS Code: built-in Ruby TextMate grammar (source.ruby) plus Ruby LSP (Shopify.ruby-lsp), which ships
the ERB grammar (text.html.erb) and emits semantic tokens. Ruby LSP declares no
semanticTokenScopes, so VS Code's standard fallbacks apply. It only emits tokens the grammar cannot
decide (lib/ruby_lsp/listeners/semantic_highlighting.rb): local variable reads -> variable,
parameter reads/writes -> parameter, receiver-less paren-less calls (except Module/Kernel special
methods) -> method, class name/superclass -> class, module name -> namespace, self -> variable.
Those keys use explicit `source.ruby <fallback>` stacks; everything else is TextMate.

RBS (intellij.ruby.rbs.*) declares no keys of its own: its highlighter reuses RUBY_* keys.
YARD tags, Gemfile and Rake have no keys either. Haml/Slim keys are in css.py; EPP/Puppet in other.py.
"""

SAMPLES = {
    'rb': ('source.ruby', r'''# frozen_string_literal: true
require 'json'

module Billing
  class Invoice < ApplicationRecord
    MAX_ITEMS = 10
    @@count = 0
    has_many :items
    attr_reader :total

    def initialize(customer, rate = 1.5)
      @customer = customer
      total = $stdout.sync ? 0x1F : 42
      tags = %w[draft paid]
      ids = [1, 2]
      opts = { mode: :fast, 'key' => "a\tb #{customer.name} \q" }
      note = <<~TEXT
        Dear customer
      TEXT
      if customer.name =~ /^(\w+)$/ then puts $1 end
      items.each { |item| total += item.price }; value = Invoice::MAX_ITEMS
      long = 1 +
        2 \
        + 3
      log(total)
    end
  end
end
'''),
}

ERB = 'text.html.erb'
RB = 'source.ruby'

MAP = {
    # ---------------------------------------------------------------- Ruby (TextMate)
    'RUBY_KEYWORD':                 ('rb', 'def'),
    'RUBY_COMMENT':                 ('rb', 'frozen_string'),
    'RUBY_STRING':                  ('rb', 'json'),
    'RUBY_INTERPOLATED_STRING':     ('rb', 'a\\tb'),
    'RUBY_ESCAPE_SEQUENCE':         ('rb', '\\t'),
    'RUBY_INVALID_ESCAPE_SEQUENCE': ('rb', '\\q'),
    'RUBY_EXPR_IN_STRING':          ('rb', '#{'),
    'RUBY_HEREDOC_ID':              ('rb', '<<~TEXT'),
    'RUBY_HEREDOC_CONTENT':         ('rb', 'Dear'),
    'RUBY_REGEXP':                  ('rb', '/^'),
    'RUBY_WORDS':                   ('rb', '%w['),
    'RUBY_SYMBOL':                  ('rb', ':fast'),
    'RUBY_HASH_KEY':                ('rb', 'mode:'),
    'RUBY_NUMBER':                  ('rb', '42'),
    'RUBY_CONSTANT':                ('rb', 'Invoice::'),
    'RUBY_CVAR':                    ('rb', '@@count'),
    'RUBY_IVAR':                    ('rb', '@customer'),
    'RUBY_GVAR':                    ('rb', '$stdout'),
    'RUBY_NTH_REF':                 ('rb', '$1'),
    'RUBY_METHOD_NAME':             ('rb', 'initialize'),
    'RUBY_IDENTIFIER':              ('rb', 'each'),
    'RUBY_SPECIFIC_CALL':           ('rb', 'attr_reader'),
    'RUBY_OPERATION_SIGN':          ('rb', '= 10'),
    'RUBY_HASH_ASSOC':              ('rb', '=>'),
    'RUBY_BRACKETS':                ('rb', '[1, 2]'),
    'RUBY_PARENTHESES':             ('rb', '(customer,'),
    'RUBY_BRACES':                  ('rb', '{ mode'),
    'RUBY_COMMA':                   ('rb', ', 2]'),
    'RUBY_DOT':                     ('rb', '.sync'),
    'RUBY_COLON':                   ('rb', '::'),
    'RUBY_SEMICOLON':               ('rb', '; value'),
    'RUBY_LINE_CONTINUATION':       ('rb', '\\\n'),
    'RUBY_BAD_CHARACTER':           RB,
    # ---------------------------------------------------------------- Ruby (Ruby LSP semantic tokens)
    'RUBY_CONSTANT_DECLARATION':    f'{RB} entity.name.type.class',
    'RUBY_PARAMETER_ID':            f'{RB} variable.parameter',
    'RUBY_LOCAL_VAR_ID':            f'{RB} variable.other.readwrite',
    'RUBY_PARAMDEF_CALL':           f'{RB} entity.name.function.member',

    # ---------------------------------------------------------------- RDoc (inside # comments)
    # VS Code's Ruby grammar does not parse RDoc markup: all of it is comment text.
    **{k: ('rb', 'frozen_string') for k in (
        'RDOC_DIRECTIVE', 'RDOC_BOLD', 'RDOC_ITALIC', 'RDOC_TYPE_WRITER', 'RDOC_HEADINGS',
        'RDOC_URL', 'RDOC_EMAIL', 'RDOC_IDENTIFIER', 'RDOC_NUMBER', 'RDOC_STRING',
        'RDOC_SYMBOL', 'RDOC_KEYWORD', 'RDOC_IVAR', 'RDOC_GVAR')},

    # ---------------------------------------------------------------- ERB (Ruby LSP's text.html.erb)
    'RHTML_SCRIPTLET_START_ID':     f'{ERB} meta.embedded.block.erb punctuation.section.embedded.begin.erb',
    'RHTML_SCRIPTLET_END_ID':       f'{ERB} meta.embedded.block.erb punctuation.section.embedded.end.erb',
    'RHTML_EXPRESSION_START_ID':    f'{ERB} meta.embedded.line.erb punctuation.section.embedded.begin.erb',
    'RHTML_EXPRESSION_END_ID':      f'{ERB} meta.embedded.line.erb punctuation.section.embedded.end.erb',
    'RHTML_OMIT_NEW_LINE_ID':       f'{ERB} meta.embedded.line.erb punctuation.section.embedded.end.erb',
    'RHTML_GRAPHQL_BLOCK_START_ID': f'{ERB} meta.embedded.block.erb punctuation.section.embedded.begin.erb',
    'RHTML_GRAPHQL_BLOCK_END_ID':   f'{ERB} meta.embedded.block.erb punctuation.section.embedded.end.erb',
    'RHTML_COMMENT_ID':             f'{ERB} comment.block.erb',
    'FLEX_ERROR_ID':                ERB,
    'RHTML_SCRIPTING_BACKGROUND_ID': ('=', 'DEFAULT_TEMPLATE_LANGUAGE_COLOR'),
}

NOTES = {
    'RUBY_CONSTANT_DECLARATION': 'explicit: Ruby LSP semantic class declaration (class name); `X = 1` would be TextMate variable.other.constant',
    'RUBY_PARAMETER_ID': 'explicit: Ruby LSP semantic parameter for reads/writes (orange). Declarations get no semantic token and are TextMate variable.parameter.function / variable.other.block (plain); usages chosen as more common',
    'RUBY_LOCAL_VAR_ID': 'explicit: Ruby LSP semantic variable for local variable reads (plain). Writes `x = 1` get no semantic token and are TextMate variable.ruby (orange); reads chosen as more common',
    'RUBY_PARAMDEF_CALL': 'explicit: Ruby LSP semantic method for receiver-less DSL calls (has_many :items, render ...)',
    'RUBY_IDENTIFIER': 'unresolved identifiers are mostly receiver calls (x.each), which Ruby LSP leaves to the grammar',
    'RUBY_BAD_CHARACTER': 'bad characters: VS Code shows them as plain text (root scope)',
    'FLEX_ERROR_ID': 'ERB lexer error: plain text (root scope), like other bad-character keys',
    'RDOC_DIRECTIVE': 'all RDOC_* keys: VS Code has no RDoc markup highlighting; plain comment colour',
    'RHTML_SCRIPTLET_START_ID': 'explicit: Ruby LSP ERB grammar (not installed here)',
    'RHTML_GRAPHQL_BLOCK_START_ID': 'explicit: <%graphql %> has no ERB grammar rule; same as scriptlet delimiters',
}
