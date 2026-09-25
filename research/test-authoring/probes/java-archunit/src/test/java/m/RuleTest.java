package m;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import org.junit.jupiter.api.Test;

class RuleTest {
    @Test
    void everyHandlerIsAnnotated() {
        JavaClasses prod = new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .importPackages("m");

        classes().that().implement(Handler.class)
            .should().beAnnotatedWith(Handles.class)
            .check(prod);
    }
}
