package m;

import static java.util.stream.Collectors.toSet;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import java.util.EnumSet;
import java.util.Set;
import org.junit.jupiter.api.Test;

class SetTest {
    @Test
    void everyKindHasAHandler() {
        JavaClasses prod = new ClassFileImporter()
            .withImportOption(new ImportOption.DoNotIncludeTests())
            .importPackages("m");

        Set<Kind> handled = prod.stream()
            .filter(c -> c.isAssignableTo(Handler.class) && !c.isInterface() && c.isAnnotatedWith(Handles.class))
            .map(c -> c.getAnnotationOfType(Handles.class).value())
            .collect(toSet());
        assertEquals(EnumSet.allOf(Kind.class), handled, "kinds with a Handler implementation");
    }
}
