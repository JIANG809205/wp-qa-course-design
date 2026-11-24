import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.annotations.Test;

import java.time.Duration;
import java.util.List;

import static org.testng.Assert.assertEquals;
import static org.testng.Assert.assertTrue;

public class RestPaginationBoundaryTest {

    private static final String BASE_URL = System.getProperty("baseUrl", "http://localhost:8080");
    private static final String API_URL = System.getProperty("apiUrl", BASE_URL + "/api/items?per_page=101");

    @Test
    public void restPaginationRejectsPerPageAboveMaximumWith400() {
        WebDriver driver = new ChromeDriver();
        try {
            driver.get(BASE_URL);

            WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

            List<?> response = wait.until(d -> {
                Object raw = ((JavascriptExecutor) d).executeAsyncScript(
                        "const url = arguments[0];" +
                        "const done = arguments[arguments.length - 1];" +
                        "fetch(url).then(async r => {" +
                        "  done([r.status, await r.text()]);" +
                        "}).catch(e => done([0, String(e)]));",
                        API_URL
                );
                return raw instanceof List ? (List<?>) raw : null;
            });

            int statusCode = ((Number) response.get(0)).intValue();
            String responseBody = String.valueOf(response.get(1));

            assertEquals(statusCode, 400, "per_page=101 must be rejected with HTTP 400");
            assertTrue(responseBody.toLowerCase().contains("error") || responseBody.contains("参数"),
                    "Response body should indicate a parameter error");
        } finally {
            driver.quit();
        }
    }
}