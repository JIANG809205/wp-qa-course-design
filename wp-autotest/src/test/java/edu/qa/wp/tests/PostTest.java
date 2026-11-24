package edu.qa.wp.tests;

import static org.testng.Assert.assertTrue;

import org.testng.annotations.Test;

import edu.qa.wp.BaseTest;
import edu.qa.wp.Config;
import edu.qa.wp.pages.AdminPage;
import edu.qa.wp.pages.LoginPage;
import io.qameta.allure.Description;
import io.qameta.allure.Epic;
import io.qameta.allure.Feature;
import io.qameta.allure.Severity;
import io.qameta.allure.SeverityLevel;
import io.qameta.allure.Story;

/** 用例集：内容管理（对应 R02 / TC-POST-001、TC-POST-004） */
@Epic("WordPress Web 测试")
@Feature("内容管理")
public class PostTest extends BaseTest {

    private AdminPage loginAsAdmin() {
        new LoginPage(driver).open().login(Config.ADMIN_USER, Config.ADMIN_PASS);
        return new AdminPage(driver);
    }

    @Test(priority = 1, description = "TC-POST-001 新建文章并保存为草稿")
    @Story("草稿保存")
    @Severity(SeverityLevel.BLOCKER)
    @Description("填写标题后点击“保存草稿”，应出现成功提示")
    public void createDraftPost() {
        AdminPage admin = loginAsAdmin();
        admin.openNewPost().waitForEditor();
        admin.typeTitle("自动化草稿-" + System.currentTimeMillis());
        admin.saveDraft();

        assertTrue(admin.hasSuccessNotice(),
                "保存草稿后应出现成功提示，实际 URL=" + admin.currentUrl());
        assertTrue(admin.bodyText().contains("草稿"),
                "页面应提示已保存为草稿");
    }

    @Test(priority = 2, description = "TC-POST-004 标题为空时保存草稿")
    @Story("边界值")
    @Severity(SeverityLevel.NORMAL)
    @Description("标题留空直接保存草稿，不应出现 500 或白屏")
    public void emptyTitleDraft() {
        AdminPage admin = loginAsAdmin();
        admin.openNewPost().waitForEditor();
        admin.typeTitle("");
        admin.saveDraft();

        assertTrue(admin.hasSuccessNotice() || admin.bodyText().contains("草稿"),
                "空标题保存草稿应有明确反馈，实际 URL=" + admin.currentUrl());
        assertTrue(driver.getTitle() != null && !driver.getTitle().isEmpty(),
                "页面不应白屏");
    }
}
