package edu.qa.wp.pages;

import java.time.Duration;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import edu.qa.wp.Config;

/** 后台通用页面：仪表盘、文章列表、新建文章 */
public class AdminPage {

    private final WebDriver driver;
    private final WebDriverWait wait;

    private final By adminBar = By.id("wpadminbar");
    private final By title = By.id("title");
    private final By publish = By.id("publish");
    private final By saveDraft = By.id("save-post");
    private final By notice = By.className("notice-success");

    public AdminPage(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(Config.WAIT_SECONDS));
    }

    public boolean hasAdminBar() {
        return !driver.findElements(adminBar).isEmpty();
    }

    public AdminPage openNewPost() {
        driver.get(Config.BASE_URL + "/wp-admin/post-new.php");
        return this;
    }

    public AdminPage waitForEditor() {
        wait.until(ExpectedConditions.presenceOfElementLocated(title));
        return this;
    }

    public AdminPage typeTitle(String text) {
        WebElement el = driver.findElement(title);
        el.clear();
        if (!text.isEmpty()) {
            el.sendKeys(text);
        }
        return this;
    }

    /** 主操作按钮的文案（管理员为“发布”，投稿者为“提交审核”，二者共用 #publish 元素） */
    public String primaryActionLabel() {
        java.util.List<WebElement> els = driver.findElements(publish);
        if (els.isEmpty()) {
            return "";
        }
        WebElement el = els.get(0);
        String value = el.getAttribute("value");
        return (value == null || value.isBlank()) ? el.getText() : value;
    }

    /** 管理员视角的“发布”按钮 */
    public boolean hasPublishButton() {
        return primaryActionLabel().contains("发布");
    }

    /** 投稿者视角的“提交复审/提交审核”按钮（WP 7.1.5 中文包为“提交复审”） */
    public boolean hasSubmitForReviewButton() {
        String label = primaryActionLabel();
        if (label.contains("复审") || label.contains("审核") || label.toLowerCase().contains("review")) {
            return true;
        }
        for (WebElement el : driver.findElements(By.cssSelector("input[type=submit], button[type=submit]"))) {
            String text = (el.getAttribute("value") == null ? "" : el.getAttribute("value")) + el.getText();
            if (text.contains("复审") || text.contains("审核") || text.toLowerCase().contains("submit for review")) {
                return true;
            }
        }
        return false;
    }

    public AdminPage saveDraft() {
        driver.findElement(saveDraft).click();
        return this;
    }

    public boolean hasSuccessNotice() {
        // 经典编辑器保存后提示在 #message / .notice 中
        for (String sel : new String[] {"#message", ".notice-success", ".notice"}) {
            if (!driver.findElements(By.cssSelector(sel)).isEmpty()) {
                return true;
            }
        }
        String body = bodyText();
        return body.contains("已更新") || body.contains("草稿已保存") || body.contains("已发布");
    }

    public String bodyText() {
        return driver.findElement(By.tagName("body")).getText();
    }

    public String currentUrl() {
        return driver.getCurrentUrl();
    }
}
