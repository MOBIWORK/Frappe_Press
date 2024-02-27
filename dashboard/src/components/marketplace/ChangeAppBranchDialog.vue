<template>
	<Dialog
		v-if="source"
		:options="{
			title: `${$t('ChangeAppBranchDialog_content_1')} ${app.title}`,
			actions: [
				{
					label: $t('Select_Branch'),
					variant: 'solid',
					loading: $resources.changeBranch.loading,
					onClick: () => $resources.changeBranch.submit()
				}
			]
		}"
		:modelValue="show"
	>
		<template v-slot:body-content>
			<select class="form-select block w-full" v-model="selectedBranch">
				<option v-for="branch in branchList()" :key="branch">
					{{ branch }}
				</option>
			</select>
		</template>
	</Dialog>
</template>

<script>
export default {
	name: 'ChangeAppBranchDialog',
	data() {
		return {
			selectedBranch: null
		};
	},
	props: ['show', 'app', 'source', 'version', 'activeBranch'],
	resources: {
		branches() {
			return {
				url: 'press.api.marketplace.branches',
				params: {
					name: this.source
				},
				auto: true
			};
		},
		changeBranch() {
			return {
				url: 'press.api.marketplace.change_branch',
				params: {
					name: this.app.name,
					source: this.source,
					version: this.version,
					to_branch: this.selectedBranch
				},
				onSuccess() {
					window.location.reload();
				},
				validate() {
					if (this.selectedBranch == this.app.branch) {
						return this.$t('ChangeAppBranchDialog_content_2');
					}
				}
			};
		}
	},
	methods: {
		branchList() {
			if (this.$resources.branches.loading || !this.$resources.branches.data) {
				return [];
			}
			return this.$resources.branches.data.map(d => d.name);
		}
	},
	mounted() {
		this.selectedBranch = this.activeBranch;
	}
};
</script>
