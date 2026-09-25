package m;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;

import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.lang.ArchRule;
import com.tngtech.archunit.library.freeze.FreezingArchRule;
import legacy.NewHandler;
import legacy.OldHandler;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;

@TestMethodOrder(MethodOrderer.MethodName.class)
class FreezeTest {
    static final ArchRule RULE = FreezingArchRule.freeze(
        classes().that().implement(Handler.class).should().beAnnotatedWith(Handles.class));

    @Test
    void a_firstCheckRecordsTheExistingViolation() {
        RULE.check(new ClassFileImporter().importClasses(OldHandler.class));
    }

    @Test
    void b_laterCheckFailsOnlyOnTheNewViolation() {
        RULE.check(new ClassFileImporter().importClasses(OldHandler.class, NewHandler.class));
    }
}
