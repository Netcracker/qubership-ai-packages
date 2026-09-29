package m;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;

import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;

/** The control for CachedImportTest: the same two rules, each over its own ClassFileImporter. */
@TestMethodOrder(MethodOrderer.MethodName.class)
class FreshImportTest {
    private static ClassFileImporter importer() {
        return new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .withImportOption(new CachedImportTest.Reads());
    }

    @Test
    void handlersAreAnnotated() {
        classes().that().implement(Handler.class).should().beAnnotatedWith(Handles.class)
            .check(importer().importPackages("m"));
    }

    @Test
    void handlersArePublic() {
        classes().that().implement(Handler.class).should().bePublic()
            .check(importer().importPackages("m"));
    }
}
