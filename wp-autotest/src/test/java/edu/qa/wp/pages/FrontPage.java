package edu.qa.wp.pages;

import java.time.Duration;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import edu.qa.wp.Config;

/** 前台文章页：用于评论提交用例 */
public class FrontPage {

    private final WebDriver driver;
    private final WebDriverWait wait;

    private final By commentBox = By.id("comment");
    private final By author = By.id("author");
    private final By email = By.id("email");
    private final By submit = By.id("submit");
    private final By comments = By.id("comments");

    public FrontPage(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(Config.WAIT_SECONDS));
    }

    /** 打开第一篇已发布文章（通过 REST 取 ID，保证有评论框） */
    public FrontPage openFirstPost() {
        driver.get(Config.BASE_URL + "/?p=1");
        return this;
    }

    public boolean hasCommentForm() {
        driver.get(Config.BASE_URL + "/");
        return !driver.findElements(By.linkText("测试文章 1000：质量保证与测试实践")).isEmpty();
    }

    public void submitComment(String name, String mail, String content) {
        WebElement box = driver.findElement(commentBox);
        box.clear();
        box.sendKeys(content);
        WebElement nameEl = driver.findElement(author);
        nameEl.clear();
        nameEl.sendKeys(name);
        WebElement mailEl = driver.findElement(email);
        mailEl.clear();
        mailEl.sendKeys(mail);
        driver.findElement(submit).click();
    }

    public String pageText() {
        return driver.findElement(By.tagName("body")).getText();
    }

    public boolean isCommentVisible(String content) {
        return !driver.findElements(comments).isEmpty()
                && driver.findElement(comments).getText().contains(content);
    }

    public String currentUrl() {
        return driver.getCurrentUrl();
    }
}
