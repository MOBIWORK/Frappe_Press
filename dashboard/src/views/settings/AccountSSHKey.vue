<template>
	<Card
		title="Khóa SSH"
		subtitle="Khóa công khai SSH liên kết với tài khoản của bạn"
		v-if="$account.team.ssh_access_enabled"
	>
		<div v-if="$account.ssh_key">
			<p class="font-mono text-sm text-gray-800">
				SHA256:{{ $account.ssh_key.ssh_fingerprint }}
			</p>
			<div class="mt-2 text-base text-gray-700">
				Đã thêm vào
				{{
					$date($account.ssh_key.creation).toLocaleString({
						month: 'short',
						day: 'numeric',
						year: 'numeric'
					})
				}}
			</div>
		</div>
		<template #actions>
			<Button v-if="!$account.ssh_key" @click="showAddNewKeyDialog = true">
				Khóa SSH mới
			</Button>
			<Button v-else @click="showAddNewKeyDialog = true">
				Thay đổi khóa SSH
			</Button>
		</template>
		<Dialog
			:options="{
				title: 'Khóa SSH mới',
				actions: [
					{
						label: 'Thêm khoá',
						variant: 'solid',
						onClick: () => $resources.saveKey.submit()
					}
				]
			}"
			v-model="showAddNewKeyDialog"
		>
			<template v-slot:body-content>
				<div class="mt-3">
					<FormControl
						:label="'Khóa SSH'"
						type="textarea"
						placeholder="Begins with 'ssh-rsa', 'ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp384', 'ecdsa-sha2-nistp521', 'ssh-ed25519', 'sk-ecdsa-sha2-nistp256@openssh.com', or 'sk-ssh-ed25519@openssh.com'"
						required
						v-model="newKey"
					/>
				</div>
				<ErrorMessage class="mt-2" :message="$resources.saveKey.error" />
			</template>
		</Dialog>
	</Card>
</template>
<script>
import { notify } from '@/utils/toast';

export default {
	name: 'AccountSSHKey',
	data() {
		return {
			showAddNewKeyDialog: false,
			newKey: null
		};
	},

	resources: {
		saveKey() {
			return {
				url: 'press.api.account.add_key',
				params: {
					key: this.newKey
				},
				onSuccess() {
					this.$account.fetchAccount();
					this.showAddNewKeyDialog = false;
					notify({
						title: 'Khóa SSH mới đã được thêm',
						icon: 'check',
						color: 'green'
					});
				}
			};
		}
	}
};
</script>
