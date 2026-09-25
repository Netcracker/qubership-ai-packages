package m;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import org.junit.jupiter.api.Test;

/** RuleTest without DoNotIncludeTests. */
class WithTestsTest {
    @Test
    void everyHandlerIsAnnotated() {
        JavaClasses all = new ClassFileImporter().importPackages("m");

        classes().that().implement(Handler.class)
            .should().beAnnotatedWith(Handles.class)
            .check(all);
    }
}
