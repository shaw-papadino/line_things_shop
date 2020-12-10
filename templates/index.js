$(function () {
    // 送信
    $('form').submit(function () {
        var msg = "送信しました";
        sendText(msg);

        return false;
    });
});
