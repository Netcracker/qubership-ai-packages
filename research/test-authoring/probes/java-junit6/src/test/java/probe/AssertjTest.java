package probe;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatCode;
import static org.assertj.core.api.Assertions.assertThatExceptionOfType;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static probe.Stream.ensureBytes;
import static probe.Stream.refuse;

import java.util.List;
import org.assertj.core.api.SoftAssertions;
import org.junit.jupiter.api.Test;

/** One AssertJ assertion per test, each failing, in the order assertj.md names them. */
class AssertjTest {
    @Test
    void isEqualTo() {
        assertThat(ensureBytes(-1)).isEqualTo(0);
    }

    @Test
    void isEqualToSwapped() {
        assertThat(0).isEqualTo(ensureBytes(-1));
    }

    @Test
    void asBefore() {
        int n = -1;
        assertThat(ensureBytes(n)).as("ensureBytes(%d)", n).isEqualTo(0);
    }

    @Test
    void asAfter() {
        int n = -1;
        assertThat(ensureBytes(n)).isEqualTo(0).as("ensureBytes(%d)", n);
    }

    @Test
    void describedAs() {
        assertThat(ensureBytes(-1)).describedAs("ensureBytes(-1)").isEqualTo(0);
    }

    @Test
    void withFailMessage() {
        assertThat(ensureBytes(-1)).withFailMessage("ensureBytes(-1) is wrong").isEqualTo(0);
    }

    @Test
    void overridingErrorMessage() {
        assertThat(ensureBytes(-1)).overridingErrorMessage("ensureBytes(-1) is wrong").isEqualTo(0);
    }

    @Test
    void isTrue() {
        int expected = 0;
        assertThat(expected == ensureBytes(-1)).isTrue();
    }

    @Test
    void contains() {
        assertThat(List.of(1, 2, 3)).contains(4);
    }

    @Test
    void assertSoftlyReportsBoth() {
        SoftAssertions.assertSoftly(softly -> {
            softly.assertThat(ensureBytes(-1)).as("first").isEqualTo(0);
            softly.assertThat(ensureBytes(-2)).as("second").isEqualTo(0);
        });
    }

    @Test
    void chainStopsAtFirst() {
        assertThat(ensureBytes(-1)).as("first").isEqualTo(0);
        assertThat(ensureBytes(-2)).as("second").isEqualTo(0);
    }

    @Test
    void thrownByOtherType() {
        assertThatThrownBy(() -> refuse(-1)).isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    void thrownByNothing() {
        assertThatThrownBy(() -> ensureBytes(-1)).isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    void exceptionOfTypeOtherType() {
        assertThatExceptionOfType(IllegalArgumentException.class).isThrownBy(() -> refuse(-1));
    }

    @Test
    void hasMessageContaining() {
        assertThatThrownBy(() -> refuse(-1)).hasMessageContaining("positive");
    }

    @Test
    void hasCauseInstanceOf() {
        assertThatThrownBy(() -> refuse(-1)).hasCauseInstanceOf(ArithmeticException.class);
    }

    @Test
    void doesNotThrowAnyException() {
        assertThatCode(() -> refuse(-1)).doesNotThrowAnyException();
    }
}
