<template>
	<Card :title="$t('api_access')" :subtitle="$t('accountapi_content_1')">
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
				{{ $t('create_new_api_key') }}
			</Button>
			<Button
				v-if="$account.user.api_key"
				@click="showCreateSecretDialog = true"
			>
				{{ $t('regenerate_api_secret') }}
			</Button>
		</template>
		<Dialog
			:options="{ title: $t('api_access') }"
			v-model="showCreateSecretDialog"
			v-on:close="createSecretdialogClosed"
		>
			<template v-slot:body-content>
				<div v-if="!$resources.createSecret.data">
					<p class="text-base">
						{{ $t('accountapi_content_2') }}
						<a href="/docs/api" class="underline">MBWCloud API</a>.
					</p>
				</div>
				<div v-if="$resources.createSecret.data">
					<p class="text-base">
						{{ $t('accountapi_content_3') }}
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
					{{ $t('create_new_api_key') }}
				</Button>
				<Button
					class="w-full"
					variant="solid"
					@click="$resources.createSecret.submit()"
					v-if="$account.user.api_key && !$resources.createSecret.data"
					:loading="$resources.createSecret.loading"
				>
					{{ $t('regenerate_api_secret') }}
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
						title: this.$t('created_new_api_secret'),
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
