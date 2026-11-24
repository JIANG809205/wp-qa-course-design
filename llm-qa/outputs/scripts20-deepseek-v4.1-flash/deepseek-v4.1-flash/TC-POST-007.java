import java.time.Duration;
import java.util.List;

import org.openqa.selenium.By;
import org.openqa.selenium.Keys;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.Test;

public class AdminArticleSearchTest {

    private WebDriver driver;

    private static final String ADMIN_ARTICLE_LIST_URL = "http://localhost:8080/admin/articles";
    private static final String SEARCH_KEYWORD = "Selenium";

    @Test
    public void searchArticlesInAdminBackendOnlyReturnsMatchingResults() {
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

        driver.get(ADMIN_ARTICLE_LIST_URL);

        By searchInputLocator = By.cssSelector("input[placeholder*='搜索'], input[name='keyword'], input[type='search']");
        WebElement searchInput = wait.until(ExpectedConditions.visibilityOfElementLocated(searchInputLocator));
        searchInput.clear();
        searchInput.sendKeys(SEARCH_KEYWORD);
        searchInput.sendKeys(Keys.ENTER);

        By resultRowsLocator = By.cssSelector("table tbody tr");
        wait.until(ExpectedConditions.numberOfElementsToBeMoreThan(resultRowsLocator, 0));

        List<WebElement> resultRows = wait.until(ExpectedConditions.visibilityOfAllElementsLocatedBy(resultRowsLocator));
        Assert.assertFalse(resultRows.isEmpty(), "Search result should not be empty");

        for (WebElement row : resultRows) {
            String rowText = row.getText();
            Assert.assertTrue(
                    rowText.contains(SEARCH_KEYWORD),
                    "Every search result should contain keyword: " + SEARCH_KEYWORD + ", but was: " + rowText
            );
        }
    }
}