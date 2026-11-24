import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedCondition;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.annotations.AfterClass;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.Test;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.time.Duration;
import java.util.List;

public class WordPressAPITest {
    private WebDriver driver;
    private WebDriverWait wait;
    private final String BASE_URL = "https://example.com";

    @BeforeClass
    public void setUp() {
        System.setProperty("webdriver.chrome.driver", "path/to/chromedriver");
        driver = new ChromeDriver();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    @Test
    public void testAnonymousRetrievePublishedPosts() throws Exception {
        driver.get(BASE_URL + "/wp-json/wp/v2/posts");

        // 显式等待：等待页面包含JSON数据中的 "status": "publish" 文本
        wait.until((ExpectedCondition<Boolean>) driver -> {
            String pageSource = driver.getPageSource();
            return pageSource.contains("\"status\":\"publish\"");
        });

        String json = driver.getPageSource();
        ObjectMapper mapper = new ObjectMapper();
        JsonNode root = mapper.readTree(json);
        List<JsonNode> posts = root.findValues("status");

        // 断言所有文章状态均为publish
        for (JsonNode status : posts) {
            assert status.asText().equals("publish") : "文章包含非发布状态";
        }
    }

    @AfterClass
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}