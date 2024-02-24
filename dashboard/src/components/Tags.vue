<template>
	<Card :title="$t('Tags')">
		<template #actions>
			<Button :label="$t('Add_Tag')" @click="showAddDialog = true" />
		</template>
		<div class="divide-y" v-if="addedTags?.length">
			<ListItem v-for="tag in addedTags" :key="tag.name" :title="tag.tag">
				<template #actions>
					<Button icon="x" @click="removeTag(tag.name)" />
				</template>
			</ListItem>
		</div>
		<div v-else class="m-4 text-center">
			<p class="text-base text-gray-500">{{ $t('No_tags_added_yet') }}</p>
		</div>
		<ErrorMessage
			:message="
				$resources.addTag.error ||
				$resources.createTag.error ||
				$resources.removeTag.error
			"
		/>
	</Card>
	<Dialog
		:options="{ title: `${$t('Add_a_New_Tag_for')} ${doctype}` }"
		v-model="showAddDialog"
	>
		<template #body-content>
			<Autocomplete
				:placeholder="$t('Tags')"
				:options="getAutocompleteOptions"
				v-model="chosenTag"
				@update:modelValue="handleAutocompleteSelection"
			/>
			<FormControl
				v-if="showNewTagInput"
				v-model="newTag"
				class="mt-4"
				:placeholder="$t('Enter_New_Tags_name')"
			/>
		</template>
		<template #actions>
			<Button variant="solid" class="w-full" @click="addTag()">{{
				showNewTagInput ? $t('Create_a_New_Tag') : $t('Add_Tag')
			}}</Button>
		</template>
	</Dialog>
</template>
<script>
export default {
	name: 'Tags',
	props: ['name', 'doctype', 'resourceTags', 'tags'],
	data() {
		return {
			showAddDialog: false,
			showNewTagInput: false,
			chosenTag: '',
			newTag: '',
			addedTags: [],
			createErrorMessage: ''
		};
	},
	resources: {
		addTag() {
			return {
				url: 'press.api.dashboard.add_tag',
				params: {
					name: this.name,
					doctype: this.doctype,
					tag: this.newTag
				},
				validate() {
					if (this.addedTags.find(t => t.name == this.newTag)) {
						return this.$t('Tag_already_added');
					}
				},
				onSuccess(d) {
					this.addedTags.push(this.tags.find(t => t.name == d));
					this.showAddDialog = false;
					this.newTag = '';
					this.chosenTag = '';
				}
			};
		},
		removeTag() {
			return {
				url: 'press.api.dashboard.remove_tag',
				onSuccess(d) {
					this.addedTags = this.addedTags.filter(t => t.name != d);
				}
			};
		},
		createTag() {
			return {
				url: 'press.api.dashboard.create_new_tag',
				params: {
					name: this.name,
					doctype: this.doctype,
					tag: this.newTag
				},
				validate() {
					if (this.tags.find(t => t.tag === this.newTag)) {
						return this.$t('Tag_already_exists');
					}
				},
				onSuccess(d) {
					this.addedTags.push({ name: d.name, tag: d.tag });
					this.showNewTagInput = false;
					this.newTag = '';
					this.chosenTag = '';
				}
			};
		}
	},
	methods: {
		addTag() {
			if (this.showNewTagInput) {
				this.$resources.createTag.submit();
			} else {
				this.$resources.addTag.submit();
			}
			this.showAddDialog = false;
		},
		removeTag(tagName) {
			this.$resources.removeTag.submit({
				name: this.name,
				doctype: this.doctype,
				tag: tagName
			});
		},
		handleAutocompleteSelection() {
			if (this.chosenTag?.value === 'new_tag') {
				this.showNewTagInput = true;
			} else {
				this.newTag = this.chosenTag?.value;
				this.showNewTagInput = false;
			}
		}
	},
	mounted() {
		this.addedTags = this.resourceTags;
	},
	computed: {
		getAutocompleteOptions() {
			return [
				{
					group: this.$t('New_Tag'),
					items: [{ label: this.$t('Create_a_New_Tag'), value: 'new_tag' }]
				},
				{
					group: this.$t('Existing_Tags'),
					items: this.tags.map(t => ({ label: t.tag, value: t.name }))
				}
			];
		}
	}
};
</script>
