define(function() {
	return {
			entityTypeLookup: {
				0: 'unknown',
				1: 'collidable',
				2: 'player',
				3: 'arrow'
			},

			hydrateEntityType: function(value) {
				return this.entityTypeLookup[value];
			}
			//@TODO: dehydrate for completness sake
	};
});