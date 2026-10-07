import java.io.IOException;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Toy "legacy" discount engine with planted quirks, used as a black-box oracle in skill evals. */
public final class DiscountEngine {

    public static void main(String[] args) throws IOException {
        if (args.length != 2) {
            System.err.println("usage: java -jar discount-engine.jar <config.json> <request.json>");
            System.exit(2);
        }
        log("engine-calls.log", args[0] + " " + args[1]);
        Object config;
        Object request;
        try {
            config = new Json(Files.readString(Path.of(args[0]), StandardCharsets.UTF_8)).parse();
            request = new Json(Files.readString(Path.of(args[1]), StandardCharsets.UTF_8)).parse();
        } catch (RuntimeException e) {
            System.out.println("{\"error\":\"bad input\"}");
            System.exit(1);
            return;
        }
        System.out.println("{\"discount\":" + evaluate(asMap(config), asMap(request)) + "}");
    }

    @SuppressWarnings("unchecked")
    static Map<String, Object> asMap(Object o) {
        if (!(o instanceof Map)) {
            throw new IllegalArgumentException("object expected");
        }
        return (Map<String, Object>) o;
    }

    static int evaluate(Map<String, Object> config, Map<String, Object> request) throws IOException {
        Map<String, Map<String, Object>> rules = new LinkedHashMap<>();
        for (Object r : (List<?>) config.getOrDefault("rules", List.of())) {
            Map<String, Object> rule = asMap(r);
            rules.put(String.valueOf(rule.get("name")), rule);
        }
        int defaultDiscount = config.get("default") == null ? 0 : ((Number) config.get("default")).intValue();
        List<Map<String, Object>> ordered = new ArrayList<>(rules.values());
        ordered.sort((a, b) -> Integer.compare(discount(b), discount(a)));
        Integer winner = null;
        try {
            for (Map<String, Object> rule : ordered) {
                if (matches(rule, request) && winner == null) {
                    winner = discount(rule);
                }
            }
        } catch (CrmUnavailable e) {
            return 0;
        }
        return winner != null ? winner : defaultDiscount;
    }

    static int discount(Map<String, Object> rule) {
        return ((Number) rule.get("discount")).intValue();
    }

    static boolean matches(Map<String, Object> rule, Map<String, Object> request) throws IOException {
        for (Object c : (List<?>) rule.getOrDefault("when", List.of())) {
            Map<String, Object> cond = asMap(c);
            if (!holds(cond, request)) {
                return false;
            }
        }
        return true;
    }

    static boolean holds(Map<String, Object> cond, Map<String, Object> request) throws IOException {
        String field = String.valueOf(cond.get("field"));
        String op = String.valueOf(cond.get("op"));
        Object expected = cond.get("value");
        switch (field) {
            case "coupon": {
                Object v = request.get("coupon");
                if (v == null) {
                    return false;
                }
                boolean eq = v.toString().trim().equalsIgnoreCase(String.valueOf(expected).trim());
                return op.equals("ne") != eq;
            }
            case "amount": {
                Object v = request.get("amount");
                if (v == null) {
                    return false;
                }
                BigDecimal actual = new BigDecimal(v.toString().trim());
                BigDecimal limit = new BigDecimal(String.valueOf(expected).trim());
                switch (op) {
                    case "eq": return actual.equals(limit);
                    case "ne": return !actual.equals(limit);
                    case "gte": return actual.compareTo(limit) >= 0;
                    case "lte": return actual.compareTo(limit) <= 0;
                    default: return false;
                }
            }
            case "category": {
                Object v = request.get("categories");
                if (v == null) {
                    return false;
                }
                String[] cats = v.toString().split(",");
                for (String cat : cats) {
                    if (cat.equalsIgnoreCase(String.valueOf(expected))) {
                        return !op.equals("ne");
                    }
                }
                return op.equals("ne");
            }
            case "tier": {
                String tier = crmTier(request.get("customerId"));
                if (tier == null) {
                    return false;
                }
                boolean eq = tier.equalsIgnoreCase(String.valueOf(expected));
                return op.equals("ne") != eq;
            }
            default:
                return false;
        }
    }

    static final class CrmUnavailable extends RuntimeException {
        CrmUnavailable() {
            super("crm unavailable");
        }
    }

    static String crmTier(Object customerId) throws IOException {
        String id = customerId == null ? "" : customerId.toString();
        log("crm-calls.log", "lookup " + id);
        if (id.startsWith("x")) {
            throw new CrmUnavailable();
        }
        switch (id) {
            case "c1": return "gold";
            case "c2": return "silver";
            case "c3": return "bronze";
            default: return null;
        }
    }

    static void log(String file, String line) throws IOException {
        Files.writeString(Path.of(file), line + System.lineSeparator(), StandardCharsets.UTF_8,
                StandardOpenOption.CREATE, StandardOpenOption.APPEND);
    }

    /** Minimal JSON reader: objects, arrays, strings, numbers (as BigDecimal text), true, false, null. */
    static final class Json {
        private final String s;
        private int i;

        Json(String s) {
            this.s = s;
        }

        Object parse() {
            Object v = value();
            ws();
            if (i != s.length()) {
                throw new IllegalArgumentException("trailing data");
            }
            return v;
        }

        private void ws() {
            while (i < s.length() && Character.isWhitespace(s.charAt(i))) {
                i++;
            }
        }

        private Object value() {
            ws();
            if (i >= s.length()) {
                throw new IllegalArgumentException("eof");
            }
            char c = s.charAt(i);
            if (c == '{') {
                i++;
                Map<String, Object> m = new LinkedHashMap<>();
                ws();
                if (s.charAt(i) == '}') {
                    i++;
                    return m;
                }
                while (true) {
                    ws();
                    String k = string();
                    ws();
                    expect(':');
                    m.put(k, value());
                    ws();
                    if (s.charAt(i) == ',') {
                        i++;
                        continue;
                    }
                    expect('}');
                    return m;
                }
            }
            if (c == '[') {
                i++;
                List<Object> l = new ArrayList<>();
                ws();
                if (s.charAt(i) == ']') {
                    i++;
                    return l;
                }
                while (true) {
                    l.add(value());
                    ws();
                    if (s.charAt(i) == ',') {
                        i++;
                        continue;
                    }
                    expect(']');
                    return l;
                }
            }
            if (c == '"') {
                return string();
            }
            if (s.startsWith("true", i)) {
                i += 4;
                return Boolean.TRUE;
            }
            if (s.startsWith("false", i)) {
                i += 5;
                return Boolean.FALSE;
            }
            if (s.startsWith("null", i)) {
                i += 4;
                return null;
            }
            int start = i;
            while (i < s.length() && "+-0123456789.eE".indexOf(s.charAt(i)) >= 0) {
                i++;
            }
            if (start == i) {
                throw new IllegalArgumentException("bad value");
            }
            return new BigDecimal(s.substring(start, i));
        }

        private void expect(char c) {
            if (i >= s.length() || s.charAt(i) != c) {
                throw new IllegalArgumentException("expected " + c);
            }
            i++;
        }

        private String string() {
            expect('"');
            StringBuilder b = new StringBuilder();
            while (s.charAt(i) != '"') {
                char c = s.charAt(i++);
                if (c == '\\') {
                    char e = s.charAt(i++);
                    switch (e) {
                        case 'n': b.append('\n'); break;
                        case 't': b.append('\t'); break;
                        case 'r': b.append('\r'); break;
                        case 'b': b.append('\b'); break;
                        case 'f': b.append('\f'); break;
                        case 'u': b.append((char) Integer.parseInt(s.substring(i, i + 4), 16)); i += 4; break;
                        default: b.append(e);
                    }
                } else {
                    b.append(c);
                }
            }
            i++;
            return b.toString();
        }
    }
}
