"""PHP family: PHP, PHPDoc, DQL (Doctrine, in PHP strings), Twig, Smarty.

PHP is TextMate only (VS Code's built-in `text.html.php` grammar, no semantic tokens). Which
IntelliJ key paints which construct was taken from PhpStorm's PhpDumbAwareAnnotatorVisitor /
PhpAnnotatorVisitor (intellij.php.frontback.impl.jar). Twig and Smarty have no VS Code grammar
installed here, so they use explicit stacks modelled on the de-facto extensions (Twig Language 2,
Smarty Template Support).
"""

PHP = r'''<?php
namespace App\Actions;

use Illuminate\Support\Str;
use App\Models\User as Member;

#[Attribute(Attribute::TARGET_CLASS)]
final class CreateUser extends BaseAction implements Runnable
{
    public const LIMIT = 0x80;
    public string $name = 'guest';
    protected array $roles = [];
    private ?int $age = null;
    public static int $count = 0;

    /**
     * Create a user.
     *
     * @param string $email The address
     * @return Member
     */
    public function handle(string $email, int $score = 42): Member
    {
        /** @var Member $member */
        $member = new Member();
        $label = "Hi {$this->name}\n" . $email . "\q";
        $raw = <<<EOT
        Body $email
        EOT;
        $out = `ls -la`;
        $$label = true;
        $lim = self::LIMIT;
        $this->save($member);
        $this->bump();
        $this->reset();
        self::$count++;
        static::register(name: $email);
        $id = strlen($email);
        $slug = Str::slug($email);
        goto done;
        done:
        return $member;
    }
}

interface Runnable {}
'''

PHP2 = r'''<p><?php echo "Hello"; ?></p>
<?php
// Sample comment
/**
 * Collection of items.
 *
 * @template TValue
 * @property string $magic
 * @method void refresh()
 * @see <b>docs</b>
 */
#[AsCommand(name: 'app:run')]
class Box
{
    public function run(): void
    {
        $this->magic;
        $x = helper($this->items[0], 3.5);
        $dql = "SELECT u FROM App\Entity\User u WHERE u.id = :id AND u.name = 'bob' AND u.age > 18, u.x";
        $q = $this->em->createQuery("SELECT u FROM User u")->where("u.id <= :id");
    }
}
'''

SAMPLES = {'php': ('text.html.php', PHP), 'php2': ('text.html.php', PHP2)}

TW = 'text.html.twig'
SM = 'text.html.smarty'

MAP = {
    # --- PHP lexical
    'PHP_TAG': ('php', '<?php', 1),
    'PHP_KEYWORD': ('php', 'return $member', 1),
    'PHP_PRIMITIVE_TYPE_HINT': ('php', 'string', 1),
    'PHP_STRING': ('php', 'guest', 1),
    'PHP_EXEC_COMMAND_ID': ('php', 'ls -la', 1),
    'PHP_HEREDOC_ID': ('php', 'EOT', 1),
    'PHP_HEREDOC_CONTENT': ('php', 'Body', 1),
    'PHP_ESCAPE_SEQUENCE': ('php', r'\n', 1),
    'PHP_INVALID_ESCAPE_SEQUENCE': ('php', r'\q', 1),
    'PHP_NUMBER': ('php', '42', 1),
    'PHP_COMMENT': ('php2', 'Sample', 1),
    'PHP_OPERATION_SIGN': ('php', '= new', 1),
    'PHP_CONCATENATION': ('php', '. $email', 1),
    'PHP_BRACES': ('php', '{', 1),
    'PHP_BRACKETS': ('php', '[];', 1),
    'PHP_PARENTHESES': ('php', '();', 1),
    'PHP_COMMA': ('php', ', int', 1),
    'PHP_SEMICOLON': ('php', ';', 1),
    'PHP_SCRIPTING_BACKGROUND': ('=', 'DEFAULT_TEMPLATE_LANGUAGE_COLOR'),
    'PHP_BAD_CHARACTER': 'text.html.php meta.embedded.block.php source.php invalid.illegal.php',
    # --- PHP names
    'PHP_IDENTIFIER': ('php', 'Illuminate', 1),
    'PHP_CLASS': ('php', 'Str::slug', 1),
    'PHP_ALIAS_REFERENCE': ('php', 'Member();', 1),
    'PHP_INTERFACE': ('php', 'Runnable {}', 1),
    'PHP_ATTRIBUTE': ('php2', 'AsCommand', 1),
    'PHP_CONSTANT': ('php', 'LIMIT;', 1),
    'PHP_FUNCTION': ('php', 'handle', 1),
    'PHP_FUNCTION_CALL': ('php2', 'helper', 1),
    'PHP_PREDEFINED SYMBOL': ('php', 'strlen', 1),
    'PHP_INSTANCE_METHOD': ('php', 'save', 1),
    'PHP_PROTECTED_INSTANCE_METHOD': ('php', 'bump', 1),
    'PHP_PRIVATE_INSTANCE_METHOD': ('php', 'reset', 1),
    'PHP_STATIC_METHOD': ('php', 'register', 1),
    'PHP_INSTANCE_FIELD': ('php2', 'items[', 1),
    'PHP_PROTECTED_INSTANCE_FIELD': ('php2', 'em->', 1),
    'PHP_PRIVATE_INSTANCE_FIELD': ('php2', 'em->', 1),
    'MAGIC_MEMBER_ACCESS': ('php2', 'magic;', 1),
    'PHP_STATIC_FIELD': ('php', 'count++', 1),
    'PHP_VAR': ('php', 'member = new', 1),
    'PHP_VAR_VAR': ('php', '$$label', 1),
    'PHP_THIS_VAR': ('php', 'this->save', 1),
    'PHP_PARAMETER': ('php', 'email, int', 1),
    'PHP_NAMED_ARGUMENT': ('php', 'name: $email', 1),
    'GOTO_LABEL': ('php', 'done:', 1),
    # --- PHPDoc
    'PHP_DOC_COMMENT_ID': ('php', 'Create a user', 1),
    'PHP_DOC_TAG': ('php', '@param', 1),
    'PHP_DOC_IDENTIFIER': ('php', 'string $email', 1),    # @param string: doc types like array/string are keyword.other.type (red)
    'PHP_DOC_PARAMETER': ('php', '$email The', 1),
    'PHP_DOC_VAR': ('php', '$member */', 1),
    'PHP_DOC_PROPERTY_IDENTIFIER': ('php2', '$magic', 1),
    'DOC_METHOD_IDENTIFIER': ('php2', 'refresh', 1),
    'DOC_TEMPLATE_PARAMETER': ('php2', 'TValue', 1),
    'PHP_MARKUP_ID': ('php2', '<b>', 1),
    # --- DQL (Doctrine query language injected in PHP strings)
    'DQL_KEYWORD': ('php2', 'SELECT', 1),
    'DQL_STRING': ('php2', 'bob', 1),
    'DQL_NUMBER': ('php2', '18', 1),
    'DQL_DOT': ('php2', '.id =', 1),
    'DQL_COMMA': ('php2', ', u.x', 1),
    'DQL_EXPR': ('php2', 'u.id <=', 1),
    'DQL_PLACEHOLDER': ('php2', ':id")', 1),
    'DQL_BAD_CHARACTER': ('=', 'PHP_BAD_CHARACTER'),
    # --- Twig (explicit: no grammar installed; Twig Language 2 scopes)
    'TWIG_COMMENT': f'{TW} comment.block.twig',
    'TWIG_KEYWORD': f'{TW} meta.tag.template.block.twig keyword.control.twig',
    'TWIG_STRING': f'{TW} meta.tag.template.value.twig string.quoted.single.twig',
    'TWIG_NUMBER': f'{TW} meta.tag.template.value.twig constant.numeric.twig',
    'TWIG_OPERATION_SIGN': f'{TW} meta.tag.template.value.twig keyword.operator.arithmetic.twig',
    'TWIG_BRACKETS': f'{TW} meta.tag.template.value.twig punctuation.section.tag.twig',
    'TWIG_IDENTIFIER': f'{TW} meta.tag.template.value.twig variable.other.twig',
    'TWIG_BACKGROUND': ('=', 'DEFAULT_TEMPLATE_LANGUAGE_COLOR'),
    'TWIG_BAD_CHARACTER': f'{TW} invalid.illegal.twig',
    # --- Smarty (explicit: no grammar installed; Smarty Template Support scopes)
    'SMARTY_COMMENT': f'{SM} comment.block.smarty',
    'SMARTY_KEYWORD': f'{SM} source.smarty keyword.control.smarty',
    'SMARTY_STRING': f'{SM} source.smarty string.quoted.single.smarty',
    'SMARTY_NUMBER': f'{SM} source.smarty constant.numeric.smarty',
    'SMARTY_OPERATION_SIGN': f'{SM} source.smarty keyword.operator.arithmetic.smarty',
    'SMARTY_BRACKETS': f'{SM} source.smarty punctuation.section.embedded.smarty',
    'SMARTY_IDENTIFIER': f'{SM} source.smarty variable.other.smarty',
    'SMARTY_BACKGROUND': ('=', 'DEFAULT_TEMPLATE_LANGUAGE_COLOR'),
    'SMARTY_BAD_CHARACTER': f'{SM} invalid.illegal.smarty',
}

NOTES = {
    'PHP_DOC_IDENTIFIER': 'one key for all doc types: VS Code colours built-in types (array, string, int) red and class names blue; built-ins are the common case in Laravel-style docblocks',
    'PHP_IDENTIFIER': 'lexer key of every IDENTIFIER token the annotator leaves alone (PhpFileSyntaxHighlighter): '
                      'use-statement paths and names, `new X`, class type hints, extends/implements (support.class / support.other.namespace '
                      '/ inherited-class: blue, inherited-class purple in GitHub Light only), plus the namespace declaration name (visitPhpNamespace; VS Code '
                      'entity.name.type.namespace, purple). Chose blue: many per file vs one namespace line',
    'PHP_CLASS': 'PhpDumbAwareAnnotatorVisitor: class declaration name (entity.name.type.class, purple) and the class '
                 'qualifier of `X::method()`, `X::$f`, `X::CONST` and `instanceof X` (support.class, blue). Chose the '
                 'qualifier (facade/static calls dominate); `use`/`new`/type-hint names are PHP_IDENTIFIER',
    'PHP_ATTRIBUTE': 'PhpStorm paints `#[`, the name and `]`; VS Code colours only the name (support.attribute); mapped to the name',
    'PHP_BAD_CHARACTER': 'explicit: invalid.illegal (no sample produces a bad character)',
    'PHP_ALIAS_REFERENCE': 'usage of an imported alias (new Member) = support.class; the `as Member` declaration '
                           'is entity.other.alias in VS Code',
    'PHP_INTERFACE': 'PhpStorm applies it to interface declarations only (references use PHP_CLASS)',
    'PHP_KEYWORD': 'keyword.control; note VS Code paints echo/print/include as support.function (blue)',
    'PHP_PARAMETER': 'VS Code PHP grammar scopes parameters as variable.other (plain foreground)',
    'PHP_INVALID_ESCAPE_SEQUENCE': 'VS Code does not flag invalid escapes; plain string colour',
    'PHP_DOC_PARAMETER': 'VS Code leaves @param/@var/@property/@method/@template names as plain doc comment text',
    'GOTO_LABEL': 'label declaration (entity.name.goto-label); `goto done` usage is support.other in VS Code',
    'DQL_KEYWORD': 'VS Code injects source.sql into PHP strings starting with SELECT/UPDATE/...; DQL keys use that',
    'DQL_EXPR': 'DQL in a string not starting with an SQL keyword is a plain string in VS Code',
    'TWIG_COMMENT': 'Twig: explicit stacks (no Twig grammar installed), Twig Language 2 scopes',
    'SMARTY_COMMENT': 'Smarty: explicit stacks (no Smarty grammar installed), Smarty Template Support scopes',
}
