const puter = require('@heyputer/puter.js').default || require('@heyputer/puter.js').puter || require('@heyputer/puter.js');
async function test() {
    try {
        const audio = await puter.ai.txt2speech("Test", { provider: "gemini", model: "gemini-2.5-flash-preview-tts", voice: "Charon" });
        console.log("Audio type:", typeof audio);
        console.log("Audio constructor:", audio.constructor.name);
        if (Buffer.isBuffer(audio)) {
            console.log("It's a buffer!");
            require('fs').writeFileSync('test_audio.mp3', audio);
        } else {
            console.log("Keys:", Object.keys(audio));
        }
    } catch(e) {
        console.error(e);
    }
}
test();