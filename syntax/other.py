"""SQL/database (incl. MongoDB, JPA QL), Go, C/C++/Objective-C, Clojure, Puppet.

Semantic highlighting is taken into account where VS Code has a language server that emits
semantic tokens with the extensions installed here: C/C++ (cpptools).
Their identifier keys use explicit `<root> <semantic fallback scope>` stacks."""

SAMPLES = {
    # ---------------------------------------------------------------- SQL (IntelliJ demo text)
    'sql': ('source.sql', r'''-- DDL section
create table crm.product (
  id numeric primary key,
  title varchar(255) character set utf8
);
/* block */
insert into product
  values (1, 'Product1');
select count(*) from crm.product;
select id as ProductID, "title", [name], @total, p.title
  from crm.product p where id = :id;
insert into t select excluded.title from new_rows;
\set content `cat data.txt`
create procedure proc() begin
outer_loop: loop leave outer_loop; end loop;
end;
select {fn now()};
'''),
    # JPA/Hibernate QL demo text; VS Code has no JPQL grammar, the SQL one is the closest
    'jpql': ('source.sql', r'''/* query */
select object(o)
  from Product o where o.id > 99999
     and o.date > {d '2010-01-01'}
     and UPPER(o.name) like 'S%'
     and o.price > :minPrice, o.qty
'''),
    'mongojson': ('jsonc', r'''{
  // line
  /* block */
  "name": "a\tb\qc",
  "ids": [1, 2.5, true, null],
  "age": {"$gt": 18}
}
'''),
    'mongojs': ('javascript', r'''db.users.find({ name: "Ann", age: { $gt: 18 } }).limit(10); // c
'''),
    'html': ('text.html.basic', r'''<div class="x"></div>
'''),
    # ---------------------------------------------------------------- Clojure
    'clj': ('source.clojure', r'''; line comment
(defn greet [user]
  (let [n (count user) c \a k :name]
    (str "Hello " user 42 true nil)))
'''),
}

PUP = 'source.puppet'

MAP = {
    # ---------------------------------------------------------------- SQL
    'SQL_KEYWORD':            ('sql', 'select'),
    'SQL_TYPE':               ('sql', 'varchar'),
    'SQL_NUMBER':             ('sql', '255'),
    'SQL_STRING':             ('sql', "Product1"),
    'SQL_COMMENT':            ('sql', '--'),
    'SQL_SEMICOLON':          ('sql', ';\nselect count'),
    'SQL_COMMA':              ('sql', ',\n  title'),
    'SQL_DOT':                ('sql', '.title\n'),
    'SQL_PARENS':             ('sql', '(*)'),
    'SQL_BRACKETS':           ('sql', '[name'),
    'SQL_BRACES':             ('sql', '{fn'),
    'SQL_IDENT':              ('sql', 'ProductID'),
    'SQL_IDENT_DELIMITED':    ('sql', '"title"'),
    'SQL_SCHEMA':             ('sql', 'crm.product;'),
    'SQL_TABLE':              ('sql', 'product\n  values'),
    'SQL_COLUMN':             ('sql', 'id as ProductID'),
    'SQL_OUTER_QUERY_COLUMN': ('=', 'SQL_COLUMN'),
    'SQL_LOCAL_ALIAS':        ('sql', 'p.title'),
    'SQL_DATABASE_OBJECT':    ('sql', 'utf8'),
    'SQL_SYNTHETIC_ENTITY':   ('sql', 'excluded'),
    'SQL_PROCEDURE':          ('sql', 'count'),
    'SQL_PARAMETER':          ('sql', ':id'),
    'SQL_VARIABLE':           ('sql', '@total'),
    'SQL_LABEL':              ('sql', 'outer_loop:'),
    'SQL_EXTERNAL_TOOL':      ('sql', '\\set'),
    'SQL_BAD_CHARACTER':      'source.sql',
    # JPA / Hibernate QL
    'QL_KEYWORD':             ('jpql', 'select'),
    'QL_STRING':              ('jpql', "'S%"),
    'QL_NUMBER':              ('jpql', '99999'),
    'QL_DATETIME':            ('jpql', "'2010"),
    'QL_OPERATION_SIGN':      ('jpql', '> 99999'),
    'QL_PARENTHS':            ('jpql', '(o)'),
    'QL_COMMA':               ('jpql', ', o.qty'),
    'QL_DOT':                 ('jpql', '.id'),
    'QL_COMMENTS':            ('jpql', '/*'),
    'QL_ENTITY':              ('jpql', 'Product'),
    'QL_ID_VARIABLE':         ('jpql', 'o.id'),
    'QL_ATTRIBUTE':           ('jpql', 'id >'),
    'QL_FUNCTION':            ('jpql', 'UPPER'),
    'QL_PARAMETER':           ('jpql', ':minPrice'),
    'QL_BAD_CHARACTER':       'source.sql',
    # MongoDB JSON
    'MONGODB.JSON.BRACES':         ('mongojson', '{'),
    'MONGODB.JSON.BRACKETS':       ('mongojson', '['),
    'MONGODB.JSON.COMMA':          ('mongojson', ', 2.5'),
    'MONGODB.JSON.COLON':          ('mongojson', ': "a'),
    'MONGODB.JSON.NUMBER':         ('mongojson', '2.5'),
    'MONGODB.JSON.STRING':         ('mongojson', 'a\\t'),
    'MONGODB.JSON.KEYWORD':        ('mongojson', 'true'),
    'MONGODB.JSON.LINE_COMMENT':   ('mongojson', '//'),
    'MONGODB.JSON.BLOCK_COMMENT':  ('mongojson', '/*'),
    'MONGODB.JSON.IDENTIFIER':     'source.json.comments meta.structure.dictionary.json.comments meta.structure.dictionary.value.json.comments',
    'MONGODB.JSON.VALID_ESCAPE':   ('mongojson', '\\t'),
    'MONGODB.JSON.INVALID_ESCAPE': ('mongojson', '\\q'),
    'MONGODB.JSON.PROPERTY_KEY':   ('mongojson', 'name'),
    'MONGODB.JSON.PARAMETER':      'source.json.comments meta.structure.dictionary.json.comments meta.structure.dictionary.value.json.comments',
    # MongoDB shell (JavaScript)
    'MONGO_JS_COMMENT':       ('mongojs', '//'),
    'MONGO_JS_STRING':        ('mongojs', 'Ann'),
    'MONGO_JS_KEYWORD':       'source.js keyword.control.js',
    'MONGO_JS_PARENS':        ('mongojs', '({'),
    'MONGO_JS_BRACKETS':      'source.js meta.array.literal.js meta.brace.square.js',
    'MONGO_JS_BRACES':        ('mongojs', '{ name'),
    'MONGO_JS_IDENT':         ('mongojs', 'users'),
    'MONGO_JS_SEMICOLON':     ('mongojs', ';'),
    'MONGO_JS_COMMA':         ('mongojs', ', age'),
    'MONGO_JS_DOT':           ('mongojs', '.users'),
    'MONGO_JS_PROPERTY_KEY':  'source.js variable.other.property',
    'MONGO_JS_DB':            ('mongojs', 'db'),


    'TAG_ATTR_KEY':          ('html', 'class'),

    # ---------------------------------------------------------------- Clojure
    'Clojure Atom':         ('clj', 'user]'),
    'Clojure Character':    ('clj', '\\a'),
    'Clojure Keyword':      ('clj', ':name'),
    'Clojure Line comment': ('clj', ';'),
    'Clojure Literal':      ('clj', 'true'),
    'Clojure Numbers':      ('clj', '42'),
    'Clojure Strings':      ('clj', 'Hello'),

    # ---------------------------------------------------------------- Puppet (no grammar here; puppet-vscode stacks)
    'PUPPET_KEYWORD':                f'{PUP} keyword.control.puppet',
    'PUPPET_CLASS':                  f'{PUP} meta.definition.class.puppet entity.name.type.class.puppet',
    'PUPPET_RESOURCE_REFERENCE':     f'{PUP} storage.type.puppet',
    'PUPPET_VARIABLE':               f'{PUP} variable.other.readwrite.global.puppet',
    'PUPPET_VARIABLE_INTERPOLATION': f'{PUP} string.quoted.double.interpolated.puppet meta.embedded.line.puppet punctuation.section.embedded.begin.puppet',
    'PUPPET_STRING':                 f'{PUP} string.quoted.double.interpolated.puppet',
    'PUPPET_SQ_STRING':              f'{PUP} string.quoted.single.puppet',
    'PUPPET_ESCAPE_SEQUENCE':        f'{PUP} string.quoted.double.interpolated.puppet constant.character.escape.puppet',
    'PUPPET_NUMBER':                 f'{PUP} constant.numeric.integer.puppet',
    'PUPPET_REGEX':                  f'{PUP} string.regexp.literal.puppet',
    'PUPPET_BLOCK_COMMENT':          f'{PUP} comment.block.puppet',
    'PUPPET_OPERATION_SIGN':         f'{PUP} keyword.operator.assignment.puppet',
    'PUPPET_BRACES':                 f'{PUP} punctuation.section.scope.puppet',
    'PUPPET_BRACKETS':               f'{PUP} punctuation.definition.array.begin.puppet',
    'PUPPET_PARENTH':                f'{PUP} punctuation.definition.parameters.begin.puppet',
    'PUPPET_COMMA':                  f'{PUP} punctuation.separator.puppet',
    'PUPPET_DOT':                    f'{PUP} punctuation.separator.method.puppet',
    'PUPPET_SEMICOLON':              f'{PUP} punctuation.terminator.puppet',
    'PUPPET_BAD_CHARACTER':          PUP,
}

NOTES = {
    'SQL_COLUMN': 'VS Code: unqualified columns plain, qualified (t.col) table-name blue; chose unqualified',
    'SQL_TABLE': 'VS Code: unqualified tables plain, schema.table blue; chose unqualified',
    'SQL_LOCAL_ALIAS': 'alias used as qualifier (p.col) -> database-name; declaration is plain',
    'SQL_LABEL': 'no SQL grammar scope for labels: plain text',
    'QL_KEYWORD': 'JPQL: no VS Code grammar; tokenised with the SQL grammar',
    'QL_DATETIME': '{d \'...\'}: the quoted part, which VS Code colours as string',
    'MONGODB.JSON.IDENTIFIER': 'explicit: unquoted identifiers are invalid JSON in VS Code; plain text',
    'MONGODB.JSON.PARAMETER': 'explicit: no JSON construct; plain text',
    'MONGO_JS_PROPERTY_KEY': 'explicit: TS semantic token property',
    'MONGO_JS_KEYWORD': 'explicit: JS keyword stack',
    'MONGO_JS_BRACKETS': 'explicit: JS array literal bracket',
    'TAG_ATTR_KEY': 'treated as a markup tag attribute name (HTML)',
    'PUPPET_KEYWORD': 'explicit (no Puppet grammar installed)',
    'PUPPET_RESOURCE_REFERENCE': 'explicit: resource type/reference as storage.type (puppet-vscode)',
    'SQL_BAD_CHARACTER': 'bad characters: VS Code shows them as plain text (root scope)',
}
