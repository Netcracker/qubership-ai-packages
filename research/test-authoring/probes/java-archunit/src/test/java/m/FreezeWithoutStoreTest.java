package m;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;

import com.tngtech.archunit.ArchConfiguration;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.library.freeze.FreezingArchRule;
import legacy.OldHandler;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;

/** FreezeTest's first check with ArchUnit's default, which does not create a missing store. */
class FreezeWithoutStoreTest {
    @AfterEach
    void restore() {
        ArchConfiguration.get().reset();
    }

    @Test
    void firstCheckWithoutAStore() {
        ArchConfiguration.get().setProperty("freeze.store.default.allowStoreCreation", "false");
        FreezingArchRule.freeze(classes().that().implement(Handler.class).should().beAnnotatedWith(Handles.class))
            .check(new ClassFileImporter().importClasses(OldHandler.class));
    }
}
