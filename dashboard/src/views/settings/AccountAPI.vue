<template>
	<Card
		title="Truy cập API"
		subtitle="Khóa API được liên kết với tài khoản của bạn"
	>
		<div v-if="$account.user.api_key">
			<p class="font-mono text-sm text-gray-800">
				<ClickToCopyField :textContent="$account.user.api_key" />
			</p>
		</div>
		<template #actions>
			<Button
				v-if="!$account.user.api_key"
				@click="showCreateSecretDialog = true"
			>
				Tạo khóa API mới
			</Button>
			<Button
				v-if="$account.user.api_key"
				@click="showCreateSecretDialog = true"
			>
				Tạo lại mã bí mật API
			</Button>
		</template>
		<Dialog
			:options="{ title: 'Truy cập API' }"
			v-model="showCreateSecretDialog"
			v-on:close="createSecretdialogClosed"
		>
			<template v-slot:body-content>
				<div v-if="!$resources.createSecret.data">
					<p class="text-base">
						Các cặp khóa và mã bí mật API có thể được sử dụng để truy cập vào
						<a href="/docs/api" class="underline">MBW Cloud API</a>.
					</p>
				</div>
				<div v-if="$resources.createSecret.data">
					<p class="text-base">
						Vui lòng sao chép mã bí mật API ngay bây giờ. Bạn sẽ không thể nhìn
						thấy nó lại!
					</p>
					<label class="block pt-2">
						<span class="mb-2 block text-sm leading-4 text-gray-700"
							>API Key</span
						>
						<ClickToCopyField
							:textContent="$resources.createSecret.data.api_key"
						/>
					</label>
					<label class="block pt-2">
						<span class="mb-2 block text-sm leading-4 text-gray-700"
							>API Secret</span
						>
						<ClickToCopyField
							:textContent="$resources.createSecret.data.api_secret"
						/>
					</label>
				</div>
				<ErrorMessage class="mt-2" :message="$resources.createSecret.error" />
			</template>

			<template #actions>
				<Button
					class="w-full"
					variant="solid"
					@click="$resources.createSecret.submit()"
					v-if="!$account.user.api_key && !$resources.createSecret.data"
					:loading="$resources.createSecret.loading"
				>
					Tạo mã khóa API mới
				</Button>
				<Button
					class="w-full"
					variant="solid"
					@click="$resources.createSecret.submit()"
					v-if="$account.user.api_key && !$resources.createSecret.data"
					:loading="$resources.createSecret.loading"
				>
					Tạo lại mã bí mật API
				</Button>
			</template>
		</Dialog>
	</Card>
</template>
<script>
import ClickToCopyField from '@/components/ClickToCopyField.vue';
import { notify } from '@/utils/toast';

export default {
	name: 'AccountAPI',
	components: {
		ClickToCopyField
	},
	data() {
		return {
			showCreateSecretDialog: false
		};
	},

	resources: {
		createSecret() {
			return {
				url: 'press.api.account.create_api_secret',
				onSuccess() {
					notify({
						title: 'Đã tạo mã bí mật API mới',
						icon: 'check',
						color: 'green'
					});
				}
			};
		}
	},
	methods: {
		createSecretdialogClosed() {
			this.$account.fetchAccount();
			this.$resources.createSecret.reset();
		}
	}
};
</script>
