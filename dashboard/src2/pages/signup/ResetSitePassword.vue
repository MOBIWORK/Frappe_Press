<template>
	<div class="flex h-screen w-screen items-center justify-center sm:bg-gray-50">
		<div class="w-full max-w-lg p-10 border border-gray-200 rounded-md bg-white sm:shadow">
            <form class="flex flex-col" @submit.prevent="submit">
                <h1 class="text-2xl font-bold text-center pb-3">{{ t('Set Password') }}</h1>
                <p class="text-sm text-gray-500 text-center pb-3">{{ t('Set a new password for your account') }}</p>
                <div class="relative mt-2">
                    <FormControl
                        :label="t('New Password')"
                        :type="showNew ? 'text' : 'password'"
                        v-model="password"
                        name="password"
                        autocomplete="new-password"
                        variant="outline"
                        required
                    />
                    <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 translate-y-[3px] text-gray-500" @click="showNew = !showNew">
                        <span v-if="showNew">
                            <svg 
                                data-v-4fa96f29="" 
                                xmlns="http://www.w3.org/2000/svg" 
                                viewBox="0 0 24 24" 
                                fill="none" 
                                stroke="currentColor" 
                                stroke-width="1.5" 
                                stroke-linecap="round" 
                                stroke-linejoin="round" 
                                class="feather feather-eye feather feather-eye shrink-0 h-4 w-4 h-4 w-4">
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                <circle cx="12" cy="12" r="3"></circle>
                            </svg>
                        </span>
                        <span v-else>
                            <svg 
                                data-v-4fa96f29="" 
                                xmlns="http://www.w3.org/2000/svg" 
                                viewBox="0 0 24 24" 
                                fill="none" 
                                stroke="currentColor" 
                                stroke-width="1.5" 
                                stroke-linecap="round" 
                                stroke-linejoin="round" 
                                class="feather feather-eye-off feather feather-eye-off shrink-0 h-4 w-4 h-4 w-4">
                                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                                <line x1="1" y1="1" x2="23" y2="23"></line>
                            </svg>
                        </span>
                    </button>
                </div>
                <div class="relative mt-4">
                    <FormControl
                        :label="t('Confirm Password')"
                        :type="showConfirm ? 'text' : 'password'"
                        v-model="confirm"
                        name="confirm_password"
                        autocomplete="new-password"
                        variant="outline"
                        required
                    />
                    <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 translate-y-[3px] text-gray-500" @click="showConfirm = !showConfirm">
                        <span v-if="showConfirm">
                            <svg 
                                data-v-4fa96f29="" 
                                xmlns="http://www.w3.org/2000/svg" 
                                viewBox="0 0 24 24" 
                                fill="none" 
                                stroke="currentColor" 
                                stroke-width="1.5" 
                                stroke-linecap="round" 
                                stroke-linejoin="round" 
                                class="feather feather-eye feather feather-eye shrink-0 h-4 w-4 h-4 w-4">
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                <circle cx="12" cy="12" r="3"></circle>
                            </svg>
                        </span>
                        <span v-else>
                            <svg 
                                data-v-4fa96f29="" 
                                xmlns="http://www.w3.org/2000/svg" 
                                viewBox="0 0 24 24" 
                                fill="none" 
                                stroke="currentColor" 
                                stroke-width="1.5" 
                                stroke-linecap="round" 
                                stroke-linejoin="round" 
                                class="feather feather-eye-off feather feather-eye-off shrink-0 h-4 w-4 h-4 w-4">
                                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                                <line x1="1" y1="1" x2="23" y2="23"></line>
                            </svg>
                        </span>
                    </button>
                </div>
                <ErrorMessage class="mt-2" :message="errorMessage" />
                <Button class="mt-6 w-full font-medium" variant="solid" type="submit" :disabled="isDisabled" :loading="loading">
                    {{ t('Confirm') }}
                </Button>
            </form>
		</div>
	</div>
</template>

<script>
import LoginBox from '../../components/auth/SaaSLoginBox.vue';
import { toast } from 'vue-sonner';
export default {
	name: 'ResetSitePassword',
	components: { LoginBox },
	data() {
		return { password: '', confirm: '', loading: false, showNew: false, showConfirm: false, errorMessage: '' };
	},
	mounted() {
		const lang = localStorage.getItem('lang');
		if (lang) {
			try { document.cookie = `preferred_language=${lang}; path=/`; } catch (e) {}
		}
	},
	computed: {
		isDisabled() { return this.loading || !this.password || this.password !== this.confirm; },
	},
	methods: {
		t(text) {
			const lang = localStorage.getItem('lang') || 'en';
			const map = {
				en: { 'Set Password': 'Set Password', 'Set a new password for your account': 'Set a new password for your account', 'New Password': 'New Password', 'Confirm Password': 'Confirm Password', 'Confirm': 'Confirm' },
				vi: { 'Set Password': 'Đặt mật khẩu', 'Set a new password for your account': 'Tạo mật khẩu mới cho tài khoản của bạn', 'New Password': 'Mật khẩu mới', 'Confirm Password': 'Xác nhận mật khẩu', 'Confirm': 'Xác nhận' },
			};
			return map[lang]?.[text] || text;
		},
		async submit() {
			this.errorMessage = '';
			if (this.password !== this.confirm || !this.password) return;
			const domain = this.$route.query.domain;
			const user = this.$route.query.user;
			if (!domain || !user) { 
				this.errorMessage = 'Missing parameters'; 
				return; 
			}
			this.loading = true;
			try {
				// Sử dụng API đổi mật khẩu trực tiếp
				const res = await fetch('/api/method/press.api.reset_password.update_password_direct', {
					method: 'POST',
					headers: { 
						'Content-Type': 'application/x-www-form-urlencoded' 
					}, 
					body: new URLSearchParams({ 
						domain, 
						user, 
						new_password: this.password, 
						confirm_password: this.confirm 
					}) 
				});
				if (!res.ok) throw new Error(await res.text());
				const data = await res.json();
				const redirect = data.message; 
				window.location.href = redirect || `https://${domain}/app/setup-wizard/0`;
			} catch (e) {
				console.error('Password reset error:', e);
				this.errorMessage = 'Password reset failed. Please try again.';
				toast.error(__('Password reset failed'));
			} finally { 
				this.loading = false; 
			}
		},
	},
};
</script>

<style scoped>
</style>


