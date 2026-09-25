package probe;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Named.named;
import static org.junit.jupiter.params.provider.Arguments.argumentSet;
import static org.junit.jupiter.params.provider.Arguments.arguments;
import static probe.Stream.ensureBytes;

import java.util.List;
import java.util.stream.Stream;
import org.junit.jupiter.api.Named;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.junit.jupiter.params.provider.ValueSource;

/** The display name of a parameterized case under each way of naming it. */
class ParameterizedCasesTest {
    @ParameterizedTest
    @ValueSource(ints = {-1, -2})
    void defaultName(int count) {
        assertEquals(0, ensureBytes(count));
    }

    @ParameterizedTest(name = "{index}: ensureBytes({0}) is refused")
    @ValueSource(ints = {-1, -2})
    void customPattern(int count) {
        assertEquals(0, ensureBytes(count));
    }

    static Stream<Named<List<Integer>>> namedLists() {
        return Stream.of(Named.of("empty list", List.of()));
    }

    @ParameterizedTest
    @MethodSource("namedLists")
    void namedOf(List<Integer> values) {
        assertEquals(1, values.size());
    }

    static Stream<Arguments> namedArguments() {
        return Stream.of(arguments(named("empty list", List.of()), 1));
    }

    @ParameterizedTest
    @MethodSource("namedArguments")
    void argumentsNamed(List<Integer> values, int size) {
        assertEquals(size, values.size());
    }

    static Stream<Arguments> argumentSets() {
        return Stream.of(argumentSet("minus one", -1), argumentSet("minus two", -2));
    }

    @ParameterizedTest
    @MethodSource("argumentSets")
    void argumentSetName(int count) {
        assertEquals(0, ensureBytes(count));
    }

    @ParameterizedTest(name = "refused: {argumentsWithNames}")
    @ValueSource(ints = {-1})
    void argumentsWithNamesPlaceholder(int count) {
        assertEquals(0, ensureBytes(count));
    }

    @ParameterizedTest(name = "{displayName} | {arguments} | {argumentSetName} | {argumentSetNameOrArgumentsWithNames}")
    @MethodSource("argumentSets")
    void otherPlaceholders(int count) {
        assertEquals(0, ensureBytes(count));
    }

    static Stream<Arguments> duplicateNames() {
        return Stream.of(argumentSet("same", -1), argumentSet("same", -2));
    }

    @ParameterizedTest
    @MethodSource("duplicateNames")
    void duplicateName(int count) {
        assertEquals(0, ensureBytes(count));
    }
}
