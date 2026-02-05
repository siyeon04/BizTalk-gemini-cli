document.addEventListener('DOMContentLoaded', () => {
    const originalText = document.getElementById('original-text');
    const charCount = document.getElementById('char-count');
    const convertBtn = document.getElementById('convert-btn');
    const targetAudience = document.getElementById('target-audience');
    const convertedResult = document.getElementById('converted-result');
    const copyBtn = document.getElementById('copy-btn');
    const loader = document.getElementById('loader');
    const btnText = convertBtn.querySelector('.btn-text');
    const feedbackArea = document.getElementById('feedback-area');
    const toast = document.getElementById('toast');

    // 실시간 글자 수 체크
    originalText.addEventListener('input', () => {
        const length = originalText.value.length;
        charCount.textContent = `${length}/500`;
        
        if (length > 500) {
            charCount.classList.add('text-red-500');
            charCount.classList.remove('text-slate-400');
        } else {
            charCount.classList.remove('text-red-500');
            charCount.classList.add('text-slate-400');
        }
    });

    // 변환 버튼 클릭 이벤트
    convertBtn.addEventListener('click', async () => {
        const text = originalText.value.trim();
        const target = targetAudience.value;

        if (!text) {
            alert('변환할 내용을 입력해주세요.');
            return;
        }

        // 로딩 상태 시작
        setLoading(true);

        try {
            const response = await fetch('/api/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text, target }),
            });

            const data = await response.json();

            if (response.ok) {
                // 성공 시 결과 표시
                displayResult(data.converted);
            } else {
                // 에러 발생 시
                throw new Error(data.error || '변환 중 오류가 발생했습니다.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert(error.message);
            displayResult('오류가 발생했습니다. 잠시 후 다시 시도해주세요.', true);
        } finally {
            // 로딩 상태 종료
            setLoading(false);
        }
    });

    // 복사 버튼 클릭 이벤트
    copyBtn.addEventListener('click', () => {
        const text = convertedResult.textContent;
        navigator.clipboard.writeText(text).then(() => {
            showToast();
        }).catch(err => {
            console.error('Failed to copy: ', err);
            alert('복사 중 오류가 발생했습니다.');
        });
    });

    // 로딩 상태 제어 함수
    function setLoading(isLoading) {
        if (isLoading) {
            convertBtn.disabled = true;
            loader.classList.remove('hidden');
            btnText.classList.add('hidden');
            
            // 결과창 로딩 상태로 변경
            convertedResult.classList.add('text-slate-400', 'flex', 'items-center', 'justify-center', 'text-center');
            convertedResult.classList.remove('text-slate-900', 'block');
            convertedResult.textContent = 'AI가 변환 중입니다...';
            
            copyBtn.disabled = true;
            feedbackArea.style.display = 'none';
        } else {
            convertBtn.disabled = false;
            loader.classList.add('hidden');
            btnText.classList.remove('hidden');
        }
    }

    // 결과 표시 함수
    function displayResult(text, isError = false) {
        if (isError) {
            convertedResult.classList.add('text-red-500', 'flex', 'items-center', 'justify-center', 'text-center');
            convertedResult.classList.remove('text-slate-900', 'text-slate-400', 'block');
            copyBtn.disabled = true;
            feedbackArea.style.display = 'none';
        } else {
            // 성공 시 레이아웃 변경: 중앙 정렬 해제, 텍스트 색상 변경
            convertedResult.classList.remove('text-slate-400', 'flex', 'items-center', 'justify-center', 'text-center');
            convertedResult.classList.add('text-slate-900', 'block');
            copyBtn.disabled = false;
            feedbackArea.style.display = 'flex';
        }
        convertedResult.textContent = text;
    }

    // 토스트 메시지 표시 함수
    function showToast() {
        toast.classList.remove('opacity-0', 'pointer-events-none');
        toast.classList.add('opacity-100');
        setTimeout(() => {
            toast.classList.add('opacity-0', 'pointer-events-none');
            toast.classList.remove('opacity-100');
        }, 2000);
    }
});
