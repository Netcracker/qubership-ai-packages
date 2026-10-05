package m;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;

import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.core.importer.Location;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;

/** Two rules over one @AnalyzeClasses; the import option prints each time the import reads AHandler. */
@AnalyzeClasses(packages = "m", importOptions = {ImportOption.DoNotIncludeTests.class, CachedImportTest.Reads.class})
class CachedImportTest {
    public static final class Reads implements ImportOption {
        @Override
        public boolean includes(Location location) {
            if (location.contains("m/AHandler.class")) {
                System.out.println("import read m/AHandler.class");
            }
            return true;
        }
    }

    @ArchTest
    static final ArchRule handlersAreAnnotated =
        classes().that().implement(Handler.class).should().beAnnotatedWith(Handles.class);

    @ArchTest
    static final ArchRule handlersArePublic =
        classes().that().implement(Handler.class).should().bePublic();
}
